use crate::progressbar;
use std::f32::consts::PI;

struct Circle {
    _x: f32,
    _y: f32,
}
impl Circle {
    fn new(x: f32, y: f32) -> Self {
        Circle { _x: x, _y: y }
    }
}

pub fn benchmark_circle() {
    let mut result: Vec<Circle> = vec![];
    let radius = 12.3;
    let points = 5_000_000;
    let angle_by_points = (PI * 2.0) / (points as f32);

    for e in 0..points {
        let x = (angle_by_points * (e as f32)).cos() * radius;
        let y = (angle_by_points * (e as f32)).sin() * radius;
        result.push(Circle::new(x, y));
    }
}
