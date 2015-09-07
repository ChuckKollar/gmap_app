// http://victorshi.com/blog/post/Use-Geolocation-API-with-Angularjs

var app = angular.module("geo", ["ui.event", "ui.map"]);
app.controller("mainController", function($scope){
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

      $.ajax({
           url :        '/',
           type :       'POST',
           contentType: 'application/json; charset=utf-8',
           dataType:    'json',
           data:        JSON.stringify(lat_lng),
           success:     function(response, textStatus, jqXHR){
                $scope.countrycode = response.countrycode;
                $scope.readings = response.readings
                console.log('Received Forcast for '+$scope.countrycode);
           },
           error:       function(jqXHR, textStatus, errorThrown){
                console.log('AJAX Failure!');
                console.log(textStatus);
                console.log(errorThrown);
           }
      });
  }
 
  $scope.getLocation();
});
