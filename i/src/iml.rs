#[derive(Debug)]
#[derive(PartialEq)]
pub enum TokenKind<'a> {
    Text(&'a str),
}

#[derive(Debug)]
#[derive(new)]
pub struct Lexer<'a> {
    src: &'a str,
    #[new(value = "1")]
    line_num: u32,
}

impl<'a> Iterator for Lexer<'a> {
    type Item = TokenKind<'a>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.line_num == 1 {
            self.line_num += 1;
            Some(TokenKind::Text("x"))
        } else {
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::iml::*;

    #[test]
    fn simplest_lexer() {
        let x = TokenKind::Text("hello");
/*        let mut l = Lexer::new("hello");
        assert_eq!(l.next().unwrap(), TokenKind::TEXT);
        assert_eq!(l.next(), None);*/
    }
}