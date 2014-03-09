var gulp = require('gulp')
var uglify = require('gulp-uglify')
var concat = require('gulp-concat')
var less = require('gulp-less')
var rename = require('gulp-rename')

var paths = {
    cdn : [
        'https://ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js'
        ,'http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js'
        ],
    less : [
        'goOut/places/static/css/goOut/master.less'
        ],
    styles: [
        'goOut/places/static/css/goOut/*'
    ]
};

gulp.task('less', function() {

    return gulp.src(paths.less)
        .pipe(less())
        // .pipe(uglify())
        .pipe(rename('public.css'))
        .pipe(gulp.dest('goOut/places/static/css'));
});

gulp.task('watch',  function() {
    // All the items that we want to watch, run them through the less command
    gulp.watch(paths.styles, ['less']);
});

gulp.task('default', ['less', 'watch'])