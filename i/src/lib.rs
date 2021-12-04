//#[macro_use]
extern crate lazy_static;
#[macro_use]
extern crate derive_new;


mod iml;

pub mod ast {
    use std::fs::File;
    use std::io::{BufRead, BufReader};

    pub struct SimpleText {
        pub text: String
    }

    pub struct Hyperlink {
        pub clickable: String,
        pub id: String,
        pub url: String
    }

    pub struct ContentRoot {
        pub children: Vec<SimpleText>
    }

    pub fn parse_line(_line: &str) {

    }

    pub fn parse_file(filename: &str) -> Result<ContentRoot, std::io::Error> {
        let file = File::open(&filename)?;
        let mut reader = BufReader::new(file);
        let mut line = String::new();
        let mut _line_num = 0u32;
        let mut cr = ContentRoot { children: Vec::new() };
        loop {
            match reader.read_line(&mut line) {
                Ok(bytes_read) => {
                    if bytes_read == 0 {
                        break Ok(cr);
                    }
                    _line_num += 1;
                    let item = SimpleText { text: String::from(&line) };
                    cr.children.push(item);
                    line.clear();
                }
                Err(err) => {
                    return Err(err);
                }
            };
        }
    }
}

#[cfg(test)]
mod tests {

    use std::path::PathBuf;
    use std::clone::Clone;

    use lazy_static::lazy_static;

    use crate::ast::*;

    #[test]
    fn simple_text_ctor() {
        let st = SimpleText { text: String::from("hello, world!") };
        assert_eq!(st.text, "hello, world!");
    }

    fn relative_data_file_path(path_fragment: &str) -> String {
        lazy_static! {
            static ref DATA_FOLDER: PathBuf = {
                let mut x = std::env::current_exe().unwrap();
                x.pop();
                x.push("../../../data/");
                x.canonicalize().unwrap()
            };
        }
        // Binary will be at something like: target/debug/deps
        let mut item = DATA_FOLDER.clone();
        item.push(&path_fragment);
        String::from(item.to_str().unwrap())
    }

    #[test]
    fn test_parse_hello() {
        parse_file(&relative_data_file_path("hello.i")).expect("whoops!");
    }
}
