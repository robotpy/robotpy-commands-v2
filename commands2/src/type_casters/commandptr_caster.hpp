
#pragma once

#include "frc2/command/Command.h"
#include "frc2/command/CommandPtr.h"
#include "frc2/command/InstantCommand.h"

#define PYBIND11_TYPE_CASTER_NO_DEFAULT(type, py_name)                                            \
public:                                                                                           \
    static constexpr auto name = py_name;                                                         \
    template <typename T_,                                                                        \
              ::pybind11::detail::enable_if_t<                                                    \
                  std::is_same<type, ::pybind11::detail::remove_cv_t<T_>>::value,                 \
                  int>                                                                            \
              = 0>                                                                                \
    static ::pybind11::handle cast(                                                               \
        T_ *src, ::pybind11::return_value_policy policy, ::pybind11::handle parent) {             \
        if (!src)                                                                                 \
            return ::pybind11::none().release();                                                  \
        if (policy == ::pybind11::return_value_policy::take_ownership) {                          \
            auto h = cast(std::move(*src), policy, parent);                                       \
            delete src;                                                                           \
            return h;                                                                             \
        }                                                                                         \
        return cast(*src, policy, parent);                                                        \
    }                                                                                             \
    operator type *() { return &value; }               /* NOLINT(bugprone-macro-parentheses) */   \
    operator type &() { return value; }                /* NOLINT(bugprone-macro-parentheses) */   \
    operator type &&() && { return std::move(value); } /* NOLINT(bugprone-macro-parentheses) */   \
    template <typename T_>                                                                        \
    using cast_op_type = ::pybind11::detail::movable_cast_op_type<T_>

namespace pybind11::detail {

template <>
struct type_caster<frc2::CommandPtr> {
    frc2::CommandPtr value = frc2::CommandPtr(std::make_unique<frc2::InstantCommand>([](){}));
    PYBIND11_TYPE_CASTER_NO_DEFAULT(frc2::CommandPtr, const_name("CommandBase"));

    bool load(handle src, bool convert) {
        if (!isinstance<frc2::CommandBase*>(src)) {
            return false;
        }

        value = frc2::CommandPtr(src.cast<std::unique_ptr<frc2::CommandBase>>());
        return true;
    }

    static handle cast(frc2::CommandPtr src, return_value_policy policy, handle parent) {
        auto c = std::move(src).Unwrap();
        return py::cast(c, policy, parent);
    }
};

} // namespace pybind11::detail