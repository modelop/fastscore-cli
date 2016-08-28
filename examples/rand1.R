
begin <- function() {
  cat("*BEGIN*")
  emit("\"output-1\"")
  emit("\"output-2\"")
  emit("\"output-3\"")
}

action <- function(datum) {
  emit(toString(runif(1)))
}

end <- function() {
  cat("*END*")
  emit("1.23")
  emit("2.34")
  emit("3.45")
}

