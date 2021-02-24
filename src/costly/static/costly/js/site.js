(function(){
  $(window).scroll(function () {
      var top = $(document).scrollTop();
      $('.corporate-jumbo').css({
        'background-position': '0px -'+(top/3).toFixed(2)+'px'
      });
      if(top > 50)
        $('.navbar').removeClass('navbar-transparent');
      else
        $('.navbar').addClass('navbar-transparent');
  }).trigger('scroll');
})();


$(document).ready(function() {
    let acknowledgeDom = document.getElementById('id_acknowledge_terms');
    let submitLoginDom = document.getElementById('submit-id-sign_in');
    if (submitLoginDom){
        submitLoginDom.disabled = true;
        // submitLoginDom.addEventListener("change", enableSubmit, false);
    }
    $("#id_acknowledge_terms").change(function() {
        let submitLoginDom = document.getElementById('submit-id-sign_in');
        submitLoginDom.disabled = submitLoginDom.disabled == true ? false : true;
    });
});



function enableSubmit(){
    let submitLoginDom = document.getElementById('submit-id-sign_in');
    submitLoginDom.disabled = submitLoginDom.disabled == true ? false : true;
}
