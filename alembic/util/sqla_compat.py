import re
from sqlalchemy import __version__
from sqlalchemy.schema import ForeignKeyConstraint, CheckConstraint
from sqlalchemy import types as sqltypes
from sqlalchemy.sql.visitors import traverse


def _safe_int(value):
    try:
        return int(value)
    except:
        return value
_vers = tuple(
    [_safe_int(x) for x in re.findall(r'(\d+|[abc]\d)', __version__)])
sqla_07 = _vers > (0, 7, 2)
sqla_079 = _vers >= (0, 7, 9)
sqla_08 = _vers >= (0, 8, 0)
sqla_083 = _vers >= (0, 8, 3)
sqla_084 = _vers >= (0, 8, 4)
sqla_09 = _vers >= (0, 9, 0)
sqla_092 = _vers >= (0, 9, 2)
sqla_094 = _vers >= (0, 9, 4)
sqla_094 = _vers >= (0, 9, 4)
sqla_099 = _vers >= (0, 9, 9)
sqla_100 = _vers >= (1, 0, 0)
sqla_105 = _vers >= (1, 0, 5)


def _table_for_constraint(constraint):
    if isinstance(constraint, ForeignKeyConstraint):
        return constraint.parent
    else:
        return constraint.table


def _columns_for_constraint(constraint):
    if isinstance(constraint, ForeignKeyConstraint):
        return [fk.parent for fk in constraint.elements]
    elif isinstance(constraint, CheckConstraint):
        return _find_columns(constraint.sqltext)
    else:
        return list(constraint.columns)


def _fk_spec(constraint):
    if sqla_100:
        source_columns = [
            constraint.columns[key].name for key in constraint.column_keys]
    else:
        source_columns = [
            element.parent.name for element in constraint.elements]

    source_table = constraint.parent.name
    source_schema = constraint.parent.schema
    target_schema = constraint.elements[0].column.table.schema
    target_table = constraint.elements[0].column.table.name
    target_columns = [element.column.name for element in constraint.elements]

    return (
        source_schema, source_table,
        source_columns, target_schema, target_table, target_columns)


def _is_type_bound(constraint):
    # this deals with SQLAlchemy #3260, don't copy CHECK constraints
    # that will be generated by the type.
    if sqla_100:
        # new feature added for #3260
        return constraint._type_bound
    else:
        # old way, look at what we know Boolean/Enum to use
        return (
            constraint._create_rule is not None and
            isinstance(
                getattr(constraint._create_rule, "target", None),
                sqltypes.SchemaType)
        )


def _find_columns(clause):
    """locate Column objects within the given expression."""

    cols = set()
    traverse(clause, {}, {'column': cols.add})
    return cols
