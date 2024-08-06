from __future__ import annotations

import sqlglot.expressions as sge

import ibis.common.exceptions as com
import ibis.expr.datashape as ds
import ibis.expr.datatypes as dt
import ibis.expr.operations as ops
from ibis.backends.sql.compilers import PostgresCompiler
from ibis.backends.sql.compilers.base import ALL_OPERATIONS
from ibis.backends.sql.datatypes import RisingWaveType
from ibis.backends.sql.dialects import RisingWave


class RisingWaveCompiler(PostgresCompiler):
    __slots__ = ()

    dialect = RisingWave
    type_mapper = RisingWaveType

    UNSUPPORTED_OPS = (
        ops.Arbitrary,
        ops.DateFromYMD,
        ops.Mode,
        ops.RandomUUID,
        *(
            op
            for op in ALL_OPERATIONS
            if issubclass(
                op, (ops.GeoSpatialUnOp, ops.GeoSpatialBinOp, ops.GeoUnaryUnion)
            )
        ),
    )

    def visit_DateNow(self, op):
        return self.cast(sge.CurrentTimestamp(), dt.date)

    def visit_First(self, op, *, arg, where, order_by):
        if not order_by:
            raise com.UnsupportedOperationError(
                "RisingWave requires an `order_by` be specified in `first`"
            )
        return self.agg.first_value(arg, where=where, order_by=order_by)

    def visit_Last(self, op, *, arg, where, order_by):
        if not order_by:
            raise com.UnsupportedOperationError(
                "RisingWave requires an `order_by` be specified in `last`"
            )
        return self.agg.last_value(arg, where=where, order_by=order_by)

    def visit_Correlation(self, op, *, left, right, how, where):
        if how == "sample":
            raise com.UnsupportedOperationError(
                "RisingWave only implements `pop` correlation coefficient"
            )
        return super().visit_Correlation(
            op, left=left, right=right, how=how, where=where
        )

    def visit_TimestampTruncate(self, op, *, arg, unit):
        unit_mapping = {
            "Y": "year",
            "Q": "quarter",
            "M": "month",
            "W": "week",
            "D": "day",
            "h": "hour",
            "m": "minute",
            "s": "second",
            "ms": "milliseconds",
            "us": "microseconds",
        }

        if (unit := unit_mapping.get(unit.short)) is None:
            raise com.UnsupportedOperationError(f"Unsupported truncate unit {unit}")

        return self.f.date_trunc(unit, arg)

    visit_TimeTruncate = visit_DateTruncate = visit_TimestampTruncate

    def visit_IntervalFromInteger(self, op, *, arg, unit):
        if op.arg.shape == ds.scalar:
            return sge.Interval(this=arg, unit=self.v[unit.name])
        elif op.arg.shape == ds.columnar:
            return arg * sge.Interval(this=sge.convert(1), unit=self.v[unit.name])
        else:
            raise ValueError("Invalid shape for converting to interval")

    def visit_NonNullLiteral(self, op, *, value, dtype):
        if dtype.is_binary():
            return self.cast("".join(map(r"\x{:0>2x}".format, value)), dt.binary)
        elif dtype.is_date():
            return self.cast(value.isoformat(), dtype)
        elif dtype.is_json():
            return sge.convert(str(value))
        return None


compiler = RisingWaveCompiler()
