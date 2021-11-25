use colored::*;

fn get_title() -> String {
    let mut the_title = String::from(env!("CARGO_PKG_NAME"));
    the_title.push_str(" (v");
    the_title.push_str(env!("CARGO_PKG_VERSION"));
    the_title.push_str("), ");
    the_title.push_str(env!("CARGO_PKG_DESCRIPTION"));
    return the_title;
}

fn parse_markdown_file(_filename: &str) {
    print_short_banner();
    println!("[ INFO ] Trying to parse {}...", _filename);
}

fn print_short_banner() {
    println!("{}", get_title());
}

fn print_long_banner() {
    println!("Written by: {}\nHomepage: {}\nUsage: i <somefile>.md",
             env!("CARGO_PKG_AUTHORS").blue(), env!("CARGO_PKG_HOMEPAGE"));
}

fn usage() {
    print_long_banner()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.len() {
        2 => parse_markdown_file(&args[1]),
        _ => {
            println!("{}", "Bad syntax.\n".red());
            usage()
        }
    }
}
