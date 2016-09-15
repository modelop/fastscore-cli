
counter <- 0

begin <- function() {
  counter <<- 100
}

action <- function(datum) {
  counter <<- counter + 1
  emit(toString(counter))
}

