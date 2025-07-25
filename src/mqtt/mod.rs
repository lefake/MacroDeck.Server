use tokio::sync::mpsc::{Sender, channel, error};
use tokio::sync::watch::error::SendError;
use tokio::sync::watch;
use std::time::Duration;
use rumqttc::{AsyncClient, Event, Incoming, MqttOptions, QoS};

pub struct MqttMsg {
    pub topic: String,
    pub retain: bool,
    pub payload: String,
}

pub struct MqttClient {
    client: AsyncClient,
    sender: Sender<MqttMsg>,
    cancel_mqtt_tx: watch::Sender<bool>,
    cancel_pub_tx: watch::Sender<bool>,
}

impl MqttClient {
    pub fn start(broker: &str, client_name: &str, port: u16, sender_cb: Sender<MqttMsg>) -> Self {
        let mut mqttoptions = MqttOptions::new(client_name, broker, port);
        mqttoptions.set_keep_alive(Duration::from_secs(5));
        let (client, mut event_loop) = AsyncClient::new(mqttoptions, 10);
        let client_clone = client.clone();

        let (cancel_mqtt_tx, cancel_mqtt_rx) = watch::channel(false);
        let (cancel_pub_tx, cancel_pub_rx) = watch::channel(false);

        let (sender, mut receiver) = channel::<MqttMsg>(32);
        _ = tokio::spawn(async move {
            while !*cancel_pub_rx.borrow() {
                while let Some(msg) = receiver.recv().await {
                    match client_clone.publish(msg.topic, QoS::AtLeastOnce, msg.retain, msg.payload).await {
                        Err(e) => eprintln!("Pub handler failed: {}", e),
                        _ => {},
                    }
                }
            }
        });

        _ = tokio::spawn(async move {
            while !*cancel_mqtt_rx.borrow() {
                while let Ok(event) = event_loop.poll().await {
                    match event {
                        Event::Incoming(Incoming::Publish(publish)) => {
                            let msg = MqttMsg {
                                topic: publish.topic,
                                retain: publish.retain,
                                payload: String::from_utf8_lossy(&publish.payload).to_string(),
                            };
                            match sender_cb.send(msg).await {
                                Err(e) => eprintln!("MQTT handler failed: {}", e),
                                _ => {}
                            }
                        }
                        _ => {}
                    }
                }
            }
        });

        MqttClient { 
            client,
            sender,
            cancel_mqtt_tx,
            cancel_pub_tx,
        }
    }

    pub async fn stop(&self) -> Result<(), SendError<bool>> {
        self.cancel_pub_tx.send(true)?;
        self.cancel_mqtt_tx.send(true)?;
        Ok(())
    } 

    pub async fn sub(&self, topic: impl Into<String>) -> Result<(), rumqttc::ClientError> {
        self.client.subscribe(topic, QoS::AtLeastOnce).await
    }

    pub async fn publish(&self, msg: MqttMsg) -> Result<(), error::SendError<MqttMsg>> {
        self.sender.send(msg).await?;
        Ok(())
    }
}