
Vue.component('loginbutton', {
    template: '\
        <div class="login-ui">\
            <div id="login-button" v-show="!UserSession.authenticated"></div>\
            <div id="login-username" v-show="UserSession.authenticated && !UserSession.loggedIn">\
                <p>\
                    <input v-model="usernameInput" type="text" placeholder="Pick a username">\
                    <button type="button" @click="register()" :disabled="!isValidName">OK</button>\
                </p>\
                <p class="username-error">{{ errorMessage }}</p>\
                <span class="tooltip">\
                    You need to pick a username before you can save and share your filters.\
                </span>\
            </div>\
            <div id="logout-button" v-show="UserSession.loggedIn">\
                <p>Signed in as <span class="username">{{ UserSession.username }}</span></p>\
                <p><a class="logout-text" @click="UserSession.signOut()">Sign Out</a></p>\
            </div>\
        </div>',

    mounted: function() {
        window.gapi.load('auth2', function() {
            var auth2 = window.gapi.auth2.init({
                client_id: '951108445762-a8btp1qpeku524l2pe9p5ldst7qqgon1.apps.googleusercontent.com',
                cookiepolicy: 'single_host_origin'
            });
            auth2.attachClickHandler(document.getElementById('login-button'), {},
                function(googleUser) { window.UserSession.onGoogleLogin(auth2); },
                function(error) { console.error(error) }
            );
            auth2.then(function() {
                if (auth2.isSignedIn.get()) {
                    window.UserSession.onGoogleLogin(auth2);
                }
            })
            console.log("Click Handler Attached");
        })
    },

    data: function() { return {
        UserSession: window.UserSession,
        usernameInput: ""
    }},

    computed: {
        isValidName: function() {
            return this.usernameInput.match(/^[a-z0-9][a-z0-9\-]*[a-z0-9]$/) !== null;
        },
        errorMessage: function() {
            if (UserSession.lastError) {
                return UserSession.lastError;
            }
            if (this.isValidName) {
                return "";
            }
            if (this.usernameInput.length < 2) {
                return "Name must be at least 2 characters long";
            }
            if (this.usernameInput.match(/^[a-z0-9\-]+$/) === null) {
                return "Only lowercase letters, numbers and - are allowed";
            }
            if (this.usernameInput.match(/^[a-z0-9].*[a-z0-9]$/) === null) {
                return "Name must not begin or end with -";
            }
            return "Unknown error";
        }
    },

    methods: {
        register: function() {
            UserSession.register(this.usernameInput);
        }
    },

    watch: {
        usernameInput: function(x) {
            UserSession.lastError = null;
        }
    }
});


(function(UserSession) {
    UserSession.authenticated = false;
    UserSession.loggedIn = false;
    UserSession.lastError = null;

    UserSession.username = "";
    UserSession.configs = [];
    UserSession.styles = [];

    UserSession.googleAuth = null;
    UserSession.googleUser = null;

    UserSession.onGoogleLogin = function(googleAuth) {
        this.googleAuth = googleAuth
        this.googleUser = googleAuth.currentUser.get();
        this.lastError = null;
        this.authenticated = true;
        this.login();
        ga('send', 'event', 'login', 'google');
    }

    UserSession.login = function() {
        axios.post('/api/filter/user/', { 'token': this.getSessionToken() })
        .then(function(response) {
            UserSession.loggedIn = true;
            UserSession.setUserData(response.data);
        })
        .catch(function(error) {
            console.warn(error);
        });
    };

    UserSession.register = function(username) {
        UserSession.lastError = null;
        axios.post('/api/filter/user/', {
            'token': this.getSessionToken(),
            'name': username
        })
        .then(function(response) {
            UserSession.loggedIn = true;
            UserSession.setUserData(response.data);
        })
        .catch(function(error) {
            console.error(error);
            if (error.status === 409) {
                UserSession.lastError = "That name is already taken";
            } else {
                UserSession.lastError = "Unknown error";
            }
        })
        ga('send', 'event', 'login', 'register');
    }

    UserSession.signOut = function() {
        UserSession.googleAuth.signOut();
        UserSession.authenticated = false;
        UserSession.loggedIn = false;
        UserSession.setUserData({
            name: '',
            configs: [],
            styles: []
        });
    }

    UserSession.setUserData = function(data) {
        this.username = data.name;
        this.configs = data.configs;
        this.styles = data.styles;
    }

    UserSession.getSessionToken = function() {
        if (this.googleUser === null) {
            return null;
        }
        return this.googleUser.getAuthResponse().id_token;
    }

}(window.UserSession = window.UserSession || {}));

console.log("UserSession exists now: ", window.UserSession);