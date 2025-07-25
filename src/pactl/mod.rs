use once_cell::sync::Lazy;
use regex::Regex;
use std::io::{Error, ErrorKind};
use std::process::Command;
use std::fmt::{self};
use std::collections::HashMap;
use std::collections::hash_map::Entry::{Occupied, Vacant};
use tokio::sync::mpsc::Sender;
use tokio::sync::Mutex;
use std::sync::Arc;

static RE_FULL_PROCCESS: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r#"Sink Input #(\d+)[\s\S]+?Mute:.*?(\S{2,3})[\s\S]+?Volume:.*?(\d+)%[\s\S]+?application\.process\.binary\s*=\s*"([^"]+)"[\s\S]+?media\.name\s*=\s*"([^"]+)""#).unwrap()
});

#[derive(Default, Debug, Clone)]
pub struct AppName {
    pub app_name: String,
    pub media_name: String,
    pub alt_media: String,
}

impl fmt::Display for AppName {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "App Name: {}, Media Name: {}, Alt Name: {}",
            self.app_name,
            self.media_name,
            self.alt_media
        )
    }
}

impl PartialEq for AppName {
    fn eq(&self, other: &Self) -> bool {
        let a = self.app_eq(other);
        let b = self.media_eq(other);
        let c = self.alt_eq(other);

        // println!("{self} vs {other} : {a}, {b}, {c}");

        self.app_eq(other) && (
            self.media_eq(other) ||
            self.alt_eq(other)
        )
    }
}

impl AppName {
    fn app_eq(&self, other: &Self) -> bool {
        self.app_name.eq(&other.app_name)
    }

    fn media_eq(&self, other: &Self) -> bool {
        self.str_contains(&self.media_name, &other.media_name)
    }

    fn alt_eq(&self, other: &Self) -> bool {
        (!self.alt_media.is_empty() && self.str_contains(&self.alt_media, &other.media_name)) ||
        (!other.alt_media.is_empty() && self.str_contains(&self.media_name, &other.alt_media))
    }

    fn str_contains(&self, str1: &String, str2: &String) -> bool {
        str1.contains(str2) || str2.contains(str1)
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct ProcessData {
    sink_id: u32,
    pub app_name: AppName,
    pub mute: bool,
    pub volume: u8,
}

impl fmt::Display for ProcessData {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Sink Input: {}, App Name: {}, Volume: {}, Mute: {}",
            self.sink_id,
            self.app_name,
            self.volume,
            self.mute,
        )
    }
}

pub struct PactlManager {
    processes: Arc<Mutex<HashMap<u32, ProcessData>>>,
    sinks: Arc<Mutex<HashMap<String, Vec<u32>>>>,
    sender_cb: Sender<ProcessData>,
}

impl PactlManager {
    pub fn new(sender_cb: Sender<ProcessData>) -> Self {
        PactlManager { 
            processes: Arc::new(Mutex::new(HashMap::new())),
            sinks: Arc::new(Mutex::new(HashMap::new())),
            sender_cb,
        }
    }

    pub async fn print(&self) {
        let processes = self.processes.lock().await;
        let sinks = self.sinks.lock().await;

        processes.iter().for_each(
            |(_, p)| {
                println!("{}", p.to_string());
            });

        sinks.iter().for_each(
            |(name, p)| {
                println!("{} : {}", name, p.len());
            });
    }

    pub async fn get_all_processes_name(&self) -> Vec<AppName> {
        let proc = self.processes.lock().await;
        return proc.iter().map(|(_, pd)| pd.app_name.clone()).collect()
    }

    // pub async fn get_app_volume(&self, app: &str) -> Option<u8> {
    //     let sinks = self.sinks.lock().await;
    //     let processes = self.processes.lock().await;

    //     // For now only the first value is taken
    //     sinks.get(app)
    //         .and_then(|id| id.get(0))
    //         .and_then(|id| processes.get(id))
    //         .map(|proc| proc.volume)
    // }

    // pub async fn get_app_mute(&self, app: &str) -> Option<bool> {
    //     let sinks = self.sinks.lock().await;
    //     let processes = self.processes.lock().await;
    
    //     // For now only the first value is taken
    //     sinks.get(app)
    //         .and_then(|id| id.get(0))
    //         .and_then(|id| processes.get(id))
    //         .map(|proc| proc.mute)
    // }

    // pub async fn set_app_volume(&self, app: &str, vol: f64) {
    //     let sinks = self.sinks.lock().await;

    //     sinks.iter()
    //         .filter(|(k, _)| k.contains(&app.to_lowercase()))
    //         .flat_map(|(_, v)| v)
    //         .for_each(|id| {
    //             let _ = self.run_pactl_cmd(format!("pactl set-sink-input-volume {} {}%", id, vol).as_str());
    //     })
    // }

    pub async fn set_app_volume(&self, app: &AppName, vol: f64) {
        let ids = self.get_id_by_appname(app).await;
        ids.iter().for_each(|id| {
            let _ = self.run_pactl_cmd(format!("pactl set-sink-input-volume {} {}%", id, vol).as_str());
        });
    }

    // pub async fn set_app_mute(&self, app: &str, mute: bool) {
    //     let sinks = self.sinks.lock().await;

    //     sinks.get(app)
    //         .iter()
    //         .flat_map(|v| v.iter())
    //         .for_each(|id| {
    //             let _ = self.run_pactl_cmd(format!("pactl set-sink-input-mute {} {}", id, if mute {"on"} else {"off"}).as_str());
    //     })
    // }

    // pub async fn toggle_app_mute(&self, app: &str) {
    //     let sinks = self.sinks.lock().await;

    //     sinks.iter()
    //         .filter(|(k, _)| k.contains(&app.to_lowercase()))
    //         .flat_map(|(_, v)| v)
    //         .for_each(|id| {
    //             let _ = self.run_pactl_cmd(format!("pactl set-sink-input-mute {} toggle", id).as_str());
    //         });
    // }

    pub async fn toggle_app_mute(&self, app: &AppName) {
        let ids = self.get_id_by_appname(app).await;
        ids.iter().for_each(|id| {
            let _ = self.run_pactl_cmd(format!("pactl set-sink-input-mute {} toggle", id).as_str());
        });
    }

    async fn get_id_by_appname(&self, app: &AppName) -> Vec<u32> {
        let processes = self.processes.lock().await;

        return processes.iter()
            .filter(|(_, process)| process.app_name.eq(app))
            .map(|(i, _)| i.clone())
            .collect();
    }

    pub async fn refresh_processes(&self) -> Result<(), Error> {
        let stdout = self.run_pactl_cmd("pactl list sink-inputs")?;
        let proc = self.get_processes(stdout);

        self.build_sink_map(&proc).await;
        self.update_map(&proc).await;

        Ok(())
    }

    fn get_processes(&self, stdout: String) -> Vec<ProcessData> {
        RE_FULL_PROCCESS
            .captures_iter(&stdout)
            .map(|cap| ProcessData {
                sink_id: cap[1].parse().unwrap_or_else(|_| panic!("Failed to parse sink id from '{}'", &cap[1])),
                mute: cap[2].contains("yes"),
                volume: cap[3].parse().unwrap_or_else(|_| panic!("Failed to parse volumesink id from '{}'", &cap[3])),
                app_name: AppName { 
                    app_name: cap[4].to_string().to_ascii_lowercase(), 
                    media_name: cap[5].to_string().to_ascii_lowercase(),
                    ..Default::default() },
            })
            .collect()
    }

    async fn build_sink_map(&self, process: &Vec<ProcessData>) {
        let mut sinks = self.sinks.lock().await;
        sinks.clear();

        process.iter().for_each(|p| {
            match sinks.entry(p.app_name.app_name.clone()) {
                Occupied(mut entry) => {
                    let v = entry.get_mut();
                    v.push(p.sink_id);
                },
                Vacant(entry) => {
                    entry.insert_entry(vec![p.sink_id]);
                }
            }
            match sinks.entry(p.app_name.media_name.clone()) {
                Occupied(mut entry) => {
                    let v = entry.get_mut();
                    v.push(p.sink_id);
                },
                Vacant(entry) => {
                    entry.insert_entry(vec![p.sink_id]);
                }
            }
        });
    }

    async fn update_map(&self, process: &Vec<ProcessData>) {
        let mut processes = self.processes.lock().await;
        let current = &processes.clone();
        processes.clear();

        for p in process {
            if let Some(old) = current.get(&p.sink_id) {
                if old == p {
                    // Nothing changed, just copy it
                    processes.insert(p.sink_id, p.clone());
                }
                else {
                    match self.sender_cb.send(p.clone()).await {
                        Err(e) => eprintln!("Error in map update {e}"),
                        _ => {}
                    };
                    processes.insert(p.sink_id, p.clone());
                }
            }
            else {
                processes.insert(p.sink_id, p.clone());
            }
        }
    }

    fn run_pactl_cmd(&self, cmd: &str) -> Result<String, Error>{
        let mut parts = cmd.split_whitespace();
        let program = match parts.next() {
            Some(p) => p,
            None => return Err(Error::new(ErrorKind::InvalidInput, "Empty command"))
        };

        let output = Command::new(program).args(parts).output()?;
        if !output.status.success() {
            return Err(Error::new(ErrorKind::Other, "pactl failed"));
        }

        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        Ok(stdout)
    }
}