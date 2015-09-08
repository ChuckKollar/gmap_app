// http://victorshi.com/blog/post/Use-Geolocation-API-with-Angularjs

var app = angular.module("geo", ["ui.event", "ui.map"]);
app.controller("mainController", function($scope, $http){
  $scope.countrycode = '';
  $scope.readings = [];

  $scope.lat = "0";
  $scope.lng = "0";
  $scope.accuracy = "0";
  $scope.error = "";
  $scope.model = { myMap: undefined };
 
  $scope.showResult = function () {
      return $scope.error == "";
  }
 
  $scope.mapOptions = {
      center: new google.maps.LatLng($scope.lat, $scope.lng),
      zoom: 15,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
  };
 
  $scope.showPosition = function (position) {
      $scope.lat = position.coords.latitude;
      $scope.lng = position.coords.longitude;
      $scope.accuracy = position.coords.accuracy;
      $scope.$apply();
 
      var latlng = new google.maps.LatLng($scope.lat, $scope.lng);
      $scope.model.myMap.setCenter(latlng);
  }
 
  $scope.showError = function (error) {
      switch (error.code) {
          case error.PERMISSION_DENIED:
              $scope.error = "User denied the request for Geolocation."
              break;
          case error.POSITION_UNAVAILABLE:
              $scope.error = "Location information is unavailable."
              break;
          case error.TIMEOUT:
              $scope.error = "The request to get user location timed out."
              break;
          case error.UNKNOWN_ERROR:
              $scope.error = "An unknown error occurred."
              break;
      }
      $scope.$apply();
  }
 
  $scope.getLocation = function () {
      if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition($scope.showPosition, $scope.showError);
      } else {
          $scope.error = "Geolocation is not supported by this browser.";
      }
  }

  // http://stackoverflow.com/questions/20323425/angular-ui-map-google-map-residing-in-html-partial-and-hidden-with-ng-if-does
  $scope.onClick = function($event, $params) {
      // send the lat and lng to the backend to get the temperature forecast...
      var latLng = $params[0].latLng;
      var lat = latLng['G'];
      var lng = latLng['K'];
      console.log( "Latitude: "+lat+" "+", longitude: "+lng);
      var lat_lng = { 'lat' : lat, 'lng' : lng };

      // https://docs.angularjs.org/api/ng/service/$http
      // don't use $.ajax() as angular will not know that it
      // needs to update the scope variables in the view...
      $http.post('/', lat_lng).
          then(function(response) {
              // this callback will be called asynchronously
              // when the response is available
              $scope.countrycode = response.data.countrycode;
              $scope.readings = response.data.readings
              console.log('Received Forcast for '+$scope.countrycode);
          }, function(response){
              // called asynchronously if an error occurs
              // or server returns response with an error status.
              console.log('AJAX Failure!');
          });
  }
 
  $scope.getLocation();
});
