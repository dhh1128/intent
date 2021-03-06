#include "core/cli/ansi_color.h"

namespace intent {
namespace core {
namespace cli {

static char const * ansi_color_names[] = {
    #define tuple(name, hi, lo) #name,
    #include "core/cli/ansi_color.tuples"
};

static char const * ansi_color_esc_seqs[] {
    #define tuple(name, hi, lo) ANSI_ESCAPE(hi, lo),
    #include "core/cli/ansi_color.tuples"
};

char const * get_ansi_color_name(unsigned which) {
    if (which <= 15) {
        return ansi_color_names[which];
    }
    return "";
}

char const * get_ansi_color_esc_seq(unsigned which) {
    if (which <= 15) {
        return ansi_color_esc_seqs[which];
    }
    return "";
}

void print_in_color(char const * txt, int file_descriptor) {
}

std::string colorize(char const * txt);

}}} // end namespace

