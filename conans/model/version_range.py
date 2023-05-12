from collections import namedtuple
from typing import Optional

from conans.errors import ConanException
from conans.model.recipe_ref import Version


_Condition = namedtuple("_Condition", ["operator", "version"])


class _ConditionSet:

    def __init__(self, expression, prerelease):
        expressions = expression.split()
        self.prerelease = prerelease
        self.conditions = []
        for e in expressions:
            e = e.strip()
            if e[-1] == "-":  # Include pre-releases
                e = e[:-1]
                self.prerelease = True
            self.conditions.extend(self._parse_expression(e))

    @staticmethod
    def _parse_expression(expression):
        if expression in ["", "*"]:
            return [_Condition(">=", Version("0.0.0"))]

        operator = expression[0]
        if operator not in (">", "<", "^", "~", "="):
            operator = "="
            index = 0
        else:
            index = 1
        if operator in (">", "<") and expression[1] == "=":
            operator += "="
            index = 2
        version = expression[index:]
        if version == "":
            raise ConanException(f"Error parsing version range {expression}")
        if operator == "~":  # tilde minor
            v = Version(version)
            index = 1 if len(v.main) > 1 else 0
            return [_Condition(">=", v), _Condition("<", v.upper_bound(index))]
        elif operator == "^":  # caret major
            v = Version(version)

            def first_non_zero(main):
                for i, m in enumerate(main):
                    if m != 0:
                        return i
                return len(main)

            initial_index = first_non_zero(v.main)
            return [_Condition(">=", v), _Condition("<", v.upper_bound(initial_index))]
        else:
            return [_Condition(operator, Version(version))]

    def _valid(self, version, conf_resolve_prepreleases):
        if version.pre and (
            conf_resolve_prepreleases is None
            and not self.prerelease
            or conf_resolve_prepreleases is not None
            and conf_resolve_prepreleases is False
        ):
            return False
        return not any(
            condition.operator == "<"
            and not version < condition.version
            or condition.operator != "<"
            and condition.operator == "<="
            and not version <= condition.version
            or condition.operator != "<"
            and condition.operator != "<="
            and condition.operator == "="
            and version != condition.version
            or condition.operator != "<"
            and condition.operator != "<="
            and condition.operator != "="
            and condition.operator == ">"
            and not version > condition.version
            or condition.operator != "<"
            and condition.operator != "<="
            and condition.operator != "="
            and condition.operator != ">"
            and condition.operator == ">="
            and not version >= condition.version
            for condition in self.conditions
        )


class VersionRange:
    def __init__(self, expression):
        self._expression = expression
        tokens = expression.split(",")
        prereleases = any("include_prerelease" in t for t in tokens[1:])
        version_expr = tokens[0]
        self.condition_sets = []
        self.condition_sets.extend(
            _ConditionSet(alternative, prereleases)
            for alternative in version_expr.split("||")
        )

    def __str__(self):
        return self._expression

    def contains(self, version: Version, resolve_prerelease: Optional[bool]):
        """
        Whether <version> is inside the version range

        :param version: Version to check against
        :param resolve_prerelease: If ``True``, ensure prereleases can be resolved in this range
        If ``False``, prerelases can NOT be resolved in this range
        If ``None``, prereleases are resolved only if this version range expression says so
        :return: Whether the version is inside the range
        """
        assert isinstance(version, Version), type(version)
        return any(
            condition_set._valid(version, resolve_prerelease)
            for condition_set in self.condition_sets
        )

