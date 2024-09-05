let autocomplete;

function initAutoComplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("id_address"),
    {
      types: ["geocode", "establishment"],
      //The code for "UK" - is "GB" ode
      componentRestrictions: { country: ["GB"] },
    }
  );
  // function to specify what should happen when the prediction is clicked
  autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
  var place = autocomplete.getPlace();

  // User did not select the prediction. Reset the input field or alert()
  if (!place.geometry) {
    document.getElementById("id_address").placeholder = "Start typing...";
  } else {
    //console.log('place name=>', place.name)
  }
  //console.log(place)
  // get the address components and assign them to the fields
  var geocoder = new google.maps.Geocoder();
  address = document.getElementById("id_address").value;
  geocoder.geocode({ address: address }, function (results, status) {
    // console.log('status ==>' , status , ' results ==>', results )

    if (status == google.maps.GeocoderStatus.OK) {
      var latitude = results[0].geometry.location.lat();
      var longitude = results[0].geometry.location.lng();

      console.log("places :::=>", place.address_components);
      $("#id_latitude").val(latitude);
      $("#id_longitude").val(longitude);
      $("#id_address").val(address);

      for (var i = 0; i < place.address_components.length; i++) {
        for (var j = 0; j < place.address_components[i].types.length; j++) {
          if (place.address_components[i].types[j] == "postal_town") {
            $("#id_city").val(place.address_components[i].long_name);
          }
          if (
            place.address_components[i].types[j] ==
            "administrative_area_level_2"
          ) {
            $("#id_state").val(place.address_components[i].long_name);
          }
          if (place.address_components[i].types[j] == "country") {
            $("#id_country").val(place.address_components[i].long_name);
          }
          if (place.address_components[i].types[j] == "postal_code") {
            $("#id_postcode").val(place.address_components[i].long_name);
          }
        }
      }
    }
  });
}

$(document).ready(function () {
  // Place the cart-item quantity to the right items on load
  $(".itemQty").each(function () {
    var the_id = $(this).attr("id");
    var qty = $(this).attr("data-qty");
    $("#" + the_id).html(qty);
  });

  // Add to Cart
  $(".add-to-cart").on("click", function (e) {
    e.preventDefault();
    product_id = $(this).attr("data-id");
    url = $(this).attr("data-url");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        if (response.status == "Success") {
          $("#cart-counter").html(response.cart_counter["cart_count"]);
          $("#qty-" + product_id).html(response.itemQty);
          //update subtotals
          cartAmounts(
            response.cart_amount["subtotal"],
            response.cart_amount["tax_dict"],
            response.cart_amount["grandtotal"]
          );

        } else {
          if (response.status == "login_required") {
            Swal.fire({
              icon: "info",
              title: response.message,

              showCancelButton: true,
              confirmButtonText: "Go to Login",
              denyButtonText: `Cancel`,
            }).then((result) => {
              /* Read more about isConfirmed, isDenied below */
              if (result.isConfirmed) {
                window.location = "/accounts/login";
              } else if (result.isDenied) {
                window.location = "/";
              }
            });
          }
          if (response.status == "Failed") {
            Swal.fire({
              icon: "error",
              title: response.message,
            });
          }
        }
      },
    });
  });

  //decrease Cart Item
  $(".decrease-cart").on("click", function (e) {
    e.preventDefault();
    product_id = $(this).attr("data-id");
    url = $(this).attr("data-url");
    cartId = $(this).attr("id");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        if (response.status == "Success") {
          $("#cart-counter").html(response.cart_counter["cart_count"]);
          $("#qty-" + product_id).html(response.itemQty);

          cartAmounts(
            response.cart_amount["subtotal"],
            response.cart_amount["tax_dict"],
            response.cart_amount["grandtotal"]
          );

          // remove item if qty is 0 in the shopping cart on  /cart/
          if (response.itemQty == 0) {
            if (window.location.pathname == "/marketplace/cart/") {
              removeCartItem(0, cartId);
              cehckEmptyCart();
            }
          }
        } else {
          if (response.status == "login_required") {
            Swal.fire({
              icon: "info",
              title: response.message,
              showCancelButton: true,
              confirmButtonText: "Go to Login",
              denyButtonText: `Cancel`,
            }).then((result) => {
              /* Read more about isConfirmed, isDenied below */
              if (result.isConfirmed) {
                window.location = "/accounts/login";
              } else if (result.isDenied) {
                window.location = "/";
              }
            });
          }
          if (response.status == "Failed") {
            Swal.fire({
              icon: "error",
              title: response.message,
            });
          }
        }
      },
    });
  });

  //Delete Cart Item

  $(".delete-cart-item").on("click", function (e) {
    e.preventDefault();
    cart_id = $(this).attr("data-id");
    url = $(this).attr("data-url");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        if (response.status == "Failed") {
          Swal.fire({
            icon: "error",
            title: response.message,
          });
        } else {
          $("#cart-counter").html(response.cart_counter["cart_count"]);
          Swal.fire(response.status, response.message, "success");

          cartAmounts(
            response.cart_amount["subtotal"],
            response.cart_amount["tax_dict"],
            response.cart_amount["grandtotal"]
          );

          removeCartItem(0, cart_id);
          cehckEmptyCart();
        }
      },
    });
  });

  //remove cart entery if quantity is 0
  function removeCartItem(cartItemQty, cart_id) {
    if (cartItemQty <= 0) {
      document.getElementById(`cart-item-${cart_id}`).remove();
    }
  }

  //check if cart is empty and display info
  function cehckEmptyCart() {
    var cartCount = document.getElementById("cart-counter").innerHTML;
    if (cartCount == 0) {
      document.getElementById("empty-cart").style.display = "block";
    }
  }

  //update cart amounts £££ $$$
  function cartAmounts(subtotal, tax_dict, grandtotal) {
    if (window.location.pathname == "/marketplace/cart/") {
      $("#subtotal").html(subtotal);
      $("#total").html(grandtotal);

      for(key1 in tax_dict){
        for(key2 in tax_dict[key1]){
          $('#tax-'+key1).html(tax_dict[key1][key2])
        }
      }

    }
  }


  // add opening hurs
  $('.add-hour').on('click', function(e){
    e.preventDefault()
    var day = document.getElementById("id_day").value
    var from_hour = document.getElementById("id_from_hour").value
    var to_hour = document.getElementById("id_to_hour").value
    var is_closed = document.getElementById("id_is_closed").checked
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
    var url = document.getElementById('add-hours-url').value


    if (is_closed){
      is_closed = 'True'
      condition = ' day != "" '  // is closed and the day has a vlue
    } else {
      is_closed ='False'
      condition =  day != '' && from_hour != '' && to_hour != ''  // is open and the day && from_hour and to_hour have a value 
    }


    if (eval(condition) ){
      $.ajax({
        type : 'POST',
        url : url ,
        data : {
          'day' : day,
          'from_hour': from_hour,
          'to_hour' : to_hour,
          'is_closed': is_closed,
          'csrfmiddlewaretoken' : csrf_token ,
        } ,
        success: function(response){
          if (response.status == "success") {
          //update ui to show newly added data
            if (response.is_closed == "closed") {
              html = `<tr id="hour-${response.id}">
                        <td><b>${response.day}</b></td><td>Closed</td>
                        <td><a href="#" data-url="/vendor/opening-hours/delete/${response.id}"  class="delete-hour" >Remove</a></td>
                      </tr>`
            } else {
              html = `<tr id="hour-${response.id}">
                        <td><b>${response.day}</b></td><td>${response.from_hour} - ${response.to_hour}</td>
                        <td><a href="#" data-url="/vendor/opening-hours/delete/${response.id}"  class="delete-hour">Remove </a> </td>
                      </tr>`
            }
          $(".opening-hours").append(html)
          document.getElementById("opening-hours").reset()
          } else {
            Swal.fire({
              icon: "error",
              title: response.message,
            });
          }
        }
      })

    } else {
      Swal.fire({
        icon: "info",
        title: "Please Fill all fields",
      });
    }
  })


//Remove Opening Hour
$(document).on('click', '.delete-hour',   function(e){
  e.preventDefault()
  url = $(this).attr('data-url');

  console.log('requesting url >> ' , url)
  $.ajax({
    type: 'GET',
    url :  url ,
    success: function(response){
      if (response.status == "success"){
        document.getElementById(`hour-${response.id}`).remove()
      }
    }
  })
})




  //-----------------   document.ready ends here   ------------------\\
});
