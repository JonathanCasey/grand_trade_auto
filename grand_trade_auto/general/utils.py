#!/usr/bin/env python3
"""
General utilities for items that are reused, but not enough in a single
category to separate into its own file/module.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""



def bypass_for_test(scope_ref, sub_id):  # pylint: disable=unused-argument
    """
    This is purposely hardcoded to always return false.  It is intended to be
    called as an 'or' condition in any `if __name__ == '__main__'` conditionals
    where unit testing is needed or similar situtions where mocking is
    difficult.

    In unit tests, this method can be mocked and replaced with a body that
    returns true for the specific location(s) required by checking both the
    `scope_ref` and `sub_id` match together.

    The `scope_ref` can take many forms, but should be consistent within each
    category and as long as designed properly, should avoid collisions by
    design.  These categories and recommended references are:
     - method: Reference to the method itself (i.e. its name without the `()`)
     - class: Reference to the class itself
     - module: `__name__` (str), which for unit tests will avoid `__main__`

    While this does allow module references, it is highly recommended to avoid
    this, as it will require reloading the module.  If really necessary, it can
    be done likely with something like `importlib.reload(package_name)`.  To a
    much lesser degree, it is also discouraged because ensuring unique `sub_id`s
    for things at module scope is harder given how spread out this can be, but
    this is easier to solve.  Could probably even be checked with CI...

    Similarly, class references (e.g. using logic for whether to define a class
    attribute or not) are also recommended to avoid for the same reasons.  If
    needed, the same solution of reloading the module should do the trick, but
    is untested.

    Args:
      scope_ref (function/class/str/?): A unique reference to a method, class,
        or module.  See above for recommended references.  Alternative scope
        categories and/or approaches are possible so long as they are unique
        within this project and will not collide with other scope categories.
      sub_id (int/str/?): Some sort of unique identifier.  This only needs to be
        unique within the scope of the method/class/module/etc referenced, as
        the method/class/module/etc reference will create a sort of "namespace"
        for the `sub_id`.

    Returns:
      (bool): Always returns False.  Only unit test mocking may change this.
    """
    return False



def list_to_quoted_element_str(items):
    return ", ".join([f"'{str(item)}'" for item in items])
