#!/usr/bin/env python3
"""
General utilities for items that are reused, but not enough in a single
category to separate into its own file/module.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""



def bypass_for_test(mod_or_meth_ref, sub_id):  # pylint: disable=unused-argument
    """
    This is purposely hardcoded to always return false.  It is intended to be
    called as an 'or' condition in any `if __name__ == '__main__'` conditionals
    where unit testing is needed or similar situtions where mocking is
    difficult.

    In unit tests, this method can be mocked and replaced with a body that
    returns true for the specific location(s) required by checking both the
    `mod_or_meth_ref` and `sub_id` match together.

    While this does allow module references, it is highly recommended to avoid
    this, as it will require reloading the module.  If really necessary, it can
    be done likely with something like `importlib.reload(package_name)`.

    Args:
      mod_or_meth_ref (function/str/?): A unique reference to a module or
        method.  For methods, passing the reference to the method itself (i.e.
        its name without the `()` to call it) is recommended.  For modules,
        `__name__` usually works since this is intended to primarily be used in
        conjunction with cases where the `__name__` being `__main__` is covered
        by the other part of the `if` statement (see above).  Alternative
        approaches are possible so long as they are unique within the project.
      sub_id (int/str/?): Some sort of unique identifier.  This only needs to be
        unique within the scope of the module or method referenced, as the
        module or method reference will create a sort of "namespace" for the
        `sub_id`.

    Returns:
      (bool): Always returns False.  Only unit test mocking may change this.
    """
    return False
