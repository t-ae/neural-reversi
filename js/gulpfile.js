"use strict"

var gulp = require("gulp");
var rename = require("gulp-rename");
var babel = require("gulp-babel");
var uglify = require('gulp-uglify');

gulp.task("default", ()=>{
  return gulp.src("./main.js")
    .pipe(rename("reversi.js"))
    .pipe(babel({
      presets: ['es2015']
    }))
    // .pipe(uglify())
    .pipe(gulp.dest("../www"));
});
