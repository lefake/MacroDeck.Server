mod pactl;
mod mqtt;
mod mapper;
use std::collections::HashMap;

use tokio::{time::{Duration, interval}};
use tokio::sync::mpsc::{channel, Receiver, error::SendError};

use pactl::{PactlManager, ProcessData, AppName};
use mqtt::{MqttClient, MqttMsg};

use crate::mapper::MqttPactl;

const MUTES_TOPIC: &str = "macrodeck/mutes";
const GAINS_TOPIC: &str = "macrodeck/gains";
const HB_TOPIC: &str = "macrodeck/hb";
const CONTROL_TOPIC: &str = "macrodeck/vm";

struct Connection {
    mqtt: MqttClient,
    pactl: PactlManager,
    mqtt_rx: Receiver<MqttMsg>,
    pactl_rx: Receiver<ProcessData>,

    connectors: MqttPactl,

    pactl_delay: u64,
    hb_delay: u64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let (mqtt_sender, mqtt_receiver) = channel::<MqttMsg>(32);
    let mqtt = MqttClient::start(
        "mqtt.subcorp",
        "test", 
        1883,
        mqtt_sender);

    mqtt.sub(MUTES_TOPIC).await?;
    mqtt.sub(GAINS_TOPIC).await?;

    let (pactl_sender, pactl_receiver) = channel::<ProcessData>(32);
    let pactl = PactlManager::new(pactl_sender);

    let configuration: HashMap<u8, AppName> = HashMap::from([
        (0, AppName {
            app_name: "firefox".to_string(),
            media_name: "spotify".to_string(),
            alt_media: "•".to_string()
        }),
        (1, AppName {
            app_name: "firefox".to_string(),
            media_name: "twitch".to_string(),
            alt_media: "audiostream".to_string()
        }),
        (2, AppName {
            app_name: "firefox".to_string(),
            media_name: "?".to_string(),
            ..Default::default()
        }),
        (3, AppName {
            app_name: "discord".to_string(),
            media_name: "*".to_string(),
            ..Default::default()
        }),
        (4, AppName {
            app_name: "*".to_string(),
            media_name: "?".to_string(),
            ..Default::default()
        }),
    ]);

    let connectors = MqttPactl::new(configuration);

    let conn = Connection {
        mqtt,
        pactl,
        mqtt_rx: mqtt_receiver,
        pactl_rx: pactl_receiver,
        connectors,
        pactl_delay: 500,
        hb_delay: 5000,
    };


    tokio::spawn(connector_task(conn));

    tokio::signal::ctrl_c().await.unwrap();
    Ok(())
}

async fn connector_task(mut connection: Connection) {
    let mut pact_interval = interval(Duration::from_millis(connection.pactl_delay));
    let mut hb_interval = interval(Duration::from_millis(connection.hb_delay));
    let mut stuff: Vec<AppName>;

    loop {
        tokio::select! {
            // Heartbeat
            _ = hb_interval.tick() => {
                let msg = MqttMsg {
                    topic: HB_TOPIC.to_string(),
                    retain: false,
                    payload: "1".to_string(),
                };

                match connection.mqtt.publish(msg).await {
                    Err(e) => eprintln!("Error to pub {}", e),
                    _ => {},
                }
            },

            // Update pactl
            _ = pact_interval.tick() => {
                _ = connection.pactl.refresh_processes().await;
                stuff = connection.pactl.get_all_processes_name().await;
                connection.connectors.update_names(stuff);
            },

            // MQTT input
            Some(msg) = connection.mqtt_rx.recv() => {
                match mqtt_parser(msg, &connection.connectors, &connection.pactl).await {
                    Err(e) => eprint!("Error in the mqtt parser {}", e),
                    _ => {}
                }
            },

            // Pactl data changed
            Some(msg) = connection.pactl_rx.recv() => {
                match pactl_parser(msg, &connection.connectors, &connection.mqtt).await {
                    Err(e) => eprint!("Error in the pactl parser {}", e),
                    _ => {}
                }
            }

            else => {
                eprintln!("All channels closed, exiting connector");
                break;
            }
        }
    }
}

async fn pactl_parser(input: ProcessData, connectors: &MqttPactl, mqtt: &MqttClient) -> Result<(), SendError<MqttMsg>>{
    match connectors.get_strip_id_from_names(input.app_name) {
        Some(id) => {
            let payload = format!("{}:{},{}", id, input.volume, input.mute as u8);

            let msg_out = MqttMsg {
                topic: CONTROL_TOPIC.to_string(),
                retain: false,
                payload: payload,
            };
            
            mqtt.publish(msg_out).await
        }
        None => return Ok(())
    }
}

async fn mqtt_parser(input: MqttMsg, connectors: &MqttPactl, pactl: &PactlManager) -> Result<(), &'static str>{
    if input.topic.eq(MUTES_TOPIC) {
        let id = input.payload.parse::<u8>()
            .map_err(|_| "Message must be a u8")?;

        for a in connectors.get_names_from_stip_id(id).iter() {
            pactl.toggle_app_mute(a).await;
        }
    }   
    else if input.topic.eq(GAINS_TOPIC) {
        let (id, gain) = gain_parser(input.payload)?;

        for a in connectors.get_names_from_stip_id(id).iter() {
            pactl.set_app_volume(a, remap_gain(gain)).await;
        }
    }
    else {
        return Err("Unknown topic received")
    }

    Ok(())
}

fn gain_parser(payload: String) -> Result<(u8, f64), &'static str> {
    let parts: Vec<&str> = payload.split(':').collect();

    if parts.len() != 2 {
        return Err("Invalid gains");
    }

    let id = parts[0].parse::<u8>()
        .map_err(|_| "First part must be a u8")?;

    let gain = parts[1].parse::<f64>()
        .map_err(|_| "First part must be a u8")?;

    Ok((id, gain))
}

fn remap_gain(value: f64) -> f64 {
    let (from_min, from_max) = (0., 100.);
    let (to_min, to_max) = (150., 0.);

    let normalized = (value - from_min) / (from_max - from_min);
    to_min + normalized * (to_max - to_min)
}