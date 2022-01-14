pub(crate) struct ProgressBar {
    percent: f32,
    percent_step: f32,
    nb_of_char: i32,
}

impl ProgressBar {
    pub fn new(min: f32, max: f32, nb_of_char: i32) -> Self {
        let step = (max - min) / 100.;
        ProgressBar {
            percent: 0.,
            percent_step: step,
            nb_of_char,
        }
    }

    pub fn get_next(&mut self) -> f32 {
        if self.is_done() {
            return 100.;
        }
        self.percent += self.percent_step;
        self.percent
    }

    pub fn reset(&mut self) {
        self.percent = 0.;
    }

    pub fn is_done(&mut self) -> bool {
        self.percent >= 100.
    }

    pub fn show(&self) {
        let done_symbole = "■";
        let pretty_much_done = "▦";
        let not_done = "□";
        let bar = format!("{:03} {}", not_done, "").replace("0", not_done);
        
    }
}
