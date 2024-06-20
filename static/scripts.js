$(document).ready(function() {
    setTimeout(function() {
        $(".flash-message").fadeOut("slow");
    }, 5000); // 5 seconds timeout for flash messages

    // Show loading screen initially and hide main content
    $('#loading-screen').show();
    $('#main-content').hide();

    // Simulate loading time
    setTimeout(function() {
        $('#loading-screen').hide();
        $('#main-content').fadeIn(1000); // Fade in main content after hiding loading screen
    }, 3000); // 3 seconds loading screen

    // Validate final round button
    $('.btn-success').click(function(e) {
        if (!allChallengesCompleted()) {
            e.preventDefault();
            alert('Complete all the challenges first.');
        }
    });

    // Function to check if all challenges are completed
    function allChallengesCompleted() {
        var challengesCompleted = true;
        $('.challenge-item').each(function() {
            var challengeId = $(this).data('challenge-id');
            if (!completedChallenges.includes(challengeId)) {
                challengesCompleted = false;
                return false; // Break out of the loop
            }
        });
        return challengesCompleted;
    }
});
