$('form[name=log_in').submit(function (e) {
  var $form = $(this);
  var $error = $form.find('.error');
  var data = $form.serialize();

  //for backend
  $.ajax({
    url: '/user/signup',
    type: 'POST',
    data: data,
    dataType: 'json',
    success: function (resp) {
      console.log(resp);
    },
    error: function (resp) {
      console.log(resp);
    },
  });

  e.preventDefault();
});
