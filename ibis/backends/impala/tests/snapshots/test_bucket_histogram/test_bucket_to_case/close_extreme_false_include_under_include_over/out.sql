SELECT
  CASE
    WHEN `t0`.`f` < 0
    THEN 0
    WHEN (
      0 <= `t0`.`f`
    ) AND (
      `t0`.`f` < 10
    )
    THEN 1
    WHEN (
      10 <= `t0`.`f`
    ) AND (
      `t0`.`f` < 25
    )
    THEN 2
    WHEN (
      25 <= `t0`.`f`
    ) AND (
      `t0`.`f` < 50
    )
    THEN 3
    WHEN 50 <= `t0`.`f`
    THEN 4
    ELSE NULL
  END AS `Bucket(f, ())`
FROM `alltypes` AS `t0`