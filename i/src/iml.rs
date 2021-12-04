#[derive(Debug)]
#[derive(PartialEq)]
pub enum TokenKind {
    Text,
}

const NOT_BEGUN: i32 = -1;

#[derive(Debug)]
pub struct Lexer<'a> {
    src: &'a str,
    kind: Option<TokenKind>,
    pub token: Option<&'a str>,
    line_idx: i32,
    line_offset: i32,
}

impl<'a> Lexer<'a> {

    pub fn new(_src: &'a str) -> Lexer<'a> {
        Lexer {
            src: _src,
            kind: None,
            token: None,
            line_idx: NOT_BEGUN,
            line_offset: NOT_BEGUN
        }
    }

    fn new_line(&mut self) {
        self.line_idx += 1;
        self.line_offset = 0;
    }

    fn finish(&mut self) {
        self.kind = None;
        self.token = None;
    }
}

impl<'a> Iterator for Lexer<'a> {
    type Item = TokenKind;

    fn next(&mut self) -> Option<Self::Item> {
        match self.line_idx {
            NOT_BEGUN => {
                self.new_line();
                Some(TokenKind::Text)
            },
            _ => {
                self.finish();
                None
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::iml::*;

    #[test]
    fn simplest_lexer() {
        let mut l = Lexer::new("hello");
        let first = l.next().unwrap();
        dbg!(first);
        //assert_eq!(first, TokenKind::Text);
        assert_eq!(l.next(), None);
    }
}