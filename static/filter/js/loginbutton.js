
// TODO: How to test google login button locally? "Popup closed by user" error...

Vue.component('loginbutton', {
    template: '\
        <div class="login-ui">\
            <div id="login-button" class="login-button" v-show="!UserSession.loggedIn">\
            </div>\
            <div id="logout-button" v-show="UserSession.loggedIn">\
                <span class="name">{{ UserSession.username }}</span>\
                <a class="logout-text" @click="UserSession.signOutGoogle()">Sign Out</a>\
            </div>\
        </div>',
    mounted: function() {
        window.gapi.load('auth2', function() {
            var auth2 = window.gapi.auth2.init({
                client_id: '951108445762-a8btp1qpeku524l2pe9p5ldst7qqgon1.apps.googleusercontent.com',
                cookiepolicy: 'single_host_origin'
            });
            auth2.attachClickHandler(document.getElementById('login-button'), {},
                function(googleUser) { window.UserSession.onGoogleLogin(googleUser); },
                function(error) { console.error(error) }
            );
            console.log("Click Handler Attached");
        })
    },
    data: function() { return {
        UserSession: window.UserSession
    }}
});


(function(UserSession) {
    UserSession.loggedIn = false;
    UserSession.username = "";
    UserSession.sessionToken = null;

    UserSession.onGoogleLogin = function(googleUser) {
        var profile = googleUser.getBasicProfile();
        this.loggedIn = true;
        this.username = profile.getName();
        this.sessionToken = googleUser.getAuthResponse().id_token;
        ga('send', 'event', 'login', 'google');
    };

}(window.UserSession = window.UserSession || {}));

console.log("UserSession exists now: ", window.UserSession);