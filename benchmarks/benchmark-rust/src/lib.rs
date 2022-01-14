mod circle;
mod progressbar;

#[cfg(test)]
mod tests {
    use crate::circle;

    #[test]
    fn it_works() {
        circle::benchmark_circle();
    }
}
