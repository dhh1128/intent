#ifndef _bcb40e4e209843fa95eaf0a3e11427d8
#define _bcb40e4e209843fa95eaf0a3e11427d8

#include "core/filesystem.h"

namespace intent {
namespace core {
namespace dev {

class sandbox
{
public:
    static filesystem::path find_root(char const * folder_within_sandbox) noexcept(false);
};

}}} // end namespace

#endif // sentry
