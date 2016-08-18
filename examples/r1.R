
library(jsonlite)

action <- function(datum) {
  point = fromJSON(datum)
  x <- point$x
  y <- point$y
  z <- point$z
  v <- x*x + y*y + z*z

  n <- trunc(rexp(1.0))
  for (i in seq(length.out = n))
    emit(toJSON(v))
}

