WITH "t1" AS (
  SELECT
    *
  FROM "leaf" AS "t0"
  WHERE
    TRUE
)
SELECT
  "t3"."key" AS "key"
FROM "t1" AS "t3"
INNER JOIN "t1" AS "t4"
  ON "t3"."key" = "t4"."key"
INNER JOIN (
  SELECT
    "t3"."key" AS "key"
  FROM "t1" AS "t3"
  INNER JOIN "t1" AS "t4"
    ON "t3"."key" = "t4"."key"
) AS "t6"
  ON "t3"."key" = "t6"."key"