$(document).ready(function() {
$(".btn-pref .btn").click(function () {
    $(".btn-pref .btn").removeClass("btn-primary").addClass("btn-default");
    // $(".tab").addClass("active"); // instead of this do the below
    $(this).removeClass("btn-default").addClass("btn-primary");
});

/* For add game button on Manage Profile */
$('#add-game-btn').click(function (){
	$('#clear-btn').show();
	$('#new-game').show();  //new-game is the create game section
	$(this).hide();
});

/* For Clear button on Manage Profile */
$('#clear-btn').click(function (){ 
	$('#add-game-btn').show();
	$(this).hide();
	$('#new-game').hide();  //new-game is the create game section
});

});
