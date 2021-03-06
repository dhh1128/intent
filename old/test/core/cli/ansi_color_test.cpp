#include "core/cli/ansi_color.h"
#include "core/cli/tty.h"

#include "gtest/gtest.h"

using namespace intent::core::cli;

TEST(ansi_color_test, names) {
    #define tuple(name, hi, lo) \
        EXPECT_STREQ(#name, get_ansi_color_name(ansi_color::name));
    #include "core/cli/ansi_color.tuples"
}

TEST(ansi_color_test, escape_sequences) {
    #define tuple(name, hi, lo) \
        EXPECT_STREQ("\x1B[" #hi ";" #lo "m", get_ansi_color_esc_seq(ansi_color::name));
    #include "core/cli/ansi_color.tuples"
}

TEST(ansi_color_test, iteration) {
    for (ansi_color i = ansi_color::black; i <= ansi_color::white; ++i) {
        ; // if this compiles, the test passes
    }
}

TEST(ansi_color_test, display_colors) {
    if (is_a_tty()) {
        for (ansi_color i = ansi_color::black; i <= ansi_color::white; ++i) {
            printf("%s%s%s %s\n", get_ansi_color_esc_seq(i),
                   get_ansi_color_name(i), RESET_COLOR, get_ansi_color_name(i));
        }
    } else {
        printf("skipped; not a tty\n");
    }
}
