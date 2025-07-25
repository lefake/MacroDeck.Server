use crate::pactl::{AppName};
use std::collections::HashMap;
use std::array::from_fn;

pub struct MqttPactl {
    configs: HashMap<u8, AppName>,
    all_names: Vec<AppName>,
    config_mapped: [Vec<AppName>; 5],
}

impl MqttPactl {
    pub fn new(configs: HashMap<u8, AppName>) -> Self {
        let all_names = Vec::new();
        
        MqttPactl { 
            configs,
            all_names,
            config_mapped: from_fn(|_| Vec::new())
        }
    }

    pub fn get_names_from_stip_id(&self, strip: u8) -> Vec<AppName> {
        self.config_mapped[strip as usize].clone()
    }

    pub fn get_strip_id_from_names(&self, name: AppName) -> Option<u8> {
        for (i, v) in self.config_mapped.iter().enumerate() {
            if v.iter().any(|n| n.eq(&name)) {
                return Some(i as u8);
            }
        }

        None
    }

    pub fn update_names(&mut self, names: Vec<AppName>) {
        self.all_names = names;
        self.all_names.retain(|obj| !obj.app_name.contains("sd_dummy"));
        let mut full = self.all_names.clone();

        // All but full wildcard
        for (strip, app) in self.configs.iter().filter(|(i, _)| **i != 5 ) {
            self.config_mapped[*strip as usize] = self.get_names_from_config(&self.all_names, app);
            full.retain(|name| !self.config_mapped[*strip as usize].iter().any(|n| name.eq(n)));
        }

        // All the rest
        self.config_mapped[4] = full.clone();

        // for i in 0..5 {
        //     println!("{i}: {:?}", self.config_mapped[i]);
        // }
        // println!("---------------------------------------------------------");
    }

    fn get_names_from_config(&self, full_names: &Vec<AppName>, conf_app: &AppName) -> Vec<AppName> {
        let mut valid_names: Vec<AppName> = Vec::new();

        // Full wildcard is handled eslewhere
        if conf_app.app_name == "*" && conf_app.media_name == "?" {
            return valid_names;
        }

        // Normal, if matches completly
        if full_names.contains(conf_app) {
            valid_names.push(conf_app.clone());
        }
        // Wildcard for all in an app_name
        else if conf_app.media_name == "*" {
            valid_names.extend(full_names.iter()
                .filter(|name | conf_app.eq(name))
                .cloned());
        }
        // Wildcard for all media_name in a specific app_name that is not part of the config
        else if conf_app.media_name == "?" {
            let same_app: Vec<&AppName> = full_names.iter().filter(|a| a.app_name == conf_app.app_name).collect();

            for a in same_app {
                if !self.configs.values().any(|obj| a.eq(obj)) {
                    valid_names.push(a.clone());
                }
            }
        }
        valid_names
    }
}