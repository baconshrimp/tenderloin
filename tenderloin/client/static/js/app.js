(function() {

  this.config(function($locationProvider) {
    $locationProvider.html5Mode(true);
  });

  this.config(function($routeProvider) {
    $routeProvider.when('/', {
      controller: 'IndexCtrl',
      templateUrl: '/partials/index.html'
    });

    $routeProvider.when('/404', {
      templateUrl: '/partials/404.html'
    });

    $routeProvider.otherwise({
      redirectTo: '/404'
    });
  });

  this.run(function(Restangular) {
    console.log(Restangular);
  });

}).call(angular.module('tenderloin', [
  'ngRoute',
  'restangular',
  'controllers'
]));
