<template>
  <v-container fill-height
    fluid>
    <v-row justify='center' align="center">
      <v-col cols="12"
      xs="12"
      sm="8"
      md="8"
      lg="6"
      xl="6">
        <v-card elevation="6">
        <v-toolbar dark color="primary">
            <v-row>
                <v-col cols='auto'>
                    <v-toolbar-title>მართვის პანელში შესვლა</v-toolbar-title>
                </v-col>
                <v-spacer></v-spacer>
                <v-col cols='auto'>
                    <v-icon x-large dark
                    >mdi-account-circle-outline</v-icon
                    >
                </v-col>
            </v-row>
        </v-toolbar>
        <!-- login form -->
        <v-form v-model="validLogin">
          <v-container class="justify-center">
            <v-row justify="center" align="center" dense>
              <v-col cols="12">
                <v-text-field
                  v-model="email"
                  :rules="emailRules"
                  placeholder="ელ.ფოსტის მისამართი"
                  name="email"
                  prepend-inner-icon="mdi-account"
                  clearable
                  
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="password"
                  :rules="passwordRules"
                  name="password"
                  placeholder="პაროლი"
                  prepend-inner-icon="mdi-lock"
                  :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  clearable
                  :type="showPassword ? 'text' : 'password'"
                  @click:append="showPassword = !showPassword"
                  required
                  v-on:keyup.enter="login"
                ></v-text-field>
              </v-col>
              
              <v-col cols="auto">
                <v-btn
                  color="primary"
                  block
                  dark
                  @click="login"
                >
                  შესვლა
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-form>
        <!-- login form -->
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "axios";
import router from "../router/index";


export default {
  name: "AdminLogin",

  data: () => ({
    alert: null,
    errorM: "",
    loading: false,
    showPassword: false,
    password: "",
    email: "",
    validLogin: true,
    passwordRules: [(v) => !!v || "გთხოვთ შეიყვანოთ პაროლი"],
    emailRules: [
      (v) => !!v || "გთხოვთ შეიყვანოთ ელ.ფოსტის მისამართი",
      (v) => /.+@.+\..+/.test(v) || "ელ.ფოსტის მისამართი უნდა შეესაბამებოდეს ნამდვილს",
    ],
  }),

  methods: {
    //handling login workflow with axios
    login() {
      axios.post('https://postal-service-test.herokuapp.com/api/token/', {
        email: this.email,
        password: this.password
      })
      .then((response) => {
        sessionStorage.setItem('access', response.data.access)
        sessionStorage.setItem('refresh', response.data.refresh)
        this.setWithExpiry('access', response.data.access, 7200000)
        //localStorage.setItem('access', response.data.access)
        //localStorage.setItem('refresh', response.data.refresh)
        this.adminPage()
      })
      .catch((error) => {
        if(error.response.data.detail == 'No active account found with the given credentials' ||
         error.response.data.detail == 'User is inactive'){
          this.errorM = 'თქვენ არ გაქვთ შესვლის უფლება'
        }
        else if(error.response.status == 401){
          this.errorM = 'შეყვანილი ელ.ფოსტის მისამართი ან პაროლი არასწორია'
        } else {
          this.errorM = error.response.data.detail
        }
        this.$toast.error(this.errorM, {
          position: "bottom-left",
          timeout: 5000,
          closeOnClick: true,
          pauseOnFocusLoss: true,
          pauseOnHover: true,
          draggable: true,
          draggablePercent: 0.6,
          showCloseButtonOnHover: false,
          hideProgressBar: false,
          closeButton: "button",
          icon: true,
          rtl: false
        });
      })
    },

    //function navigate clinet to admin page
    adminPage() {
      router.push({ path: "/" }).catch((err) => {
        // Ignore the vuex err regarding  navigating to the page they are already on.
        if (
          err.name !== "NavigationDuplicated" &&
          !err.message.includes(
            "Avoided redundant navigation to current location"
          )
        ) {
          // But print any other errors to the console
          console.log(err);
        }
      });
    },
    
    //function navigate clinet to admin page
    loginPage() {
      router.push({ path: "/login" }).catch((err) => {
        // Ignore the vuex err regarding  navigating to the page they are already on.
        if (
          err.name !== "NavigationDuplicated" &&
          !err.message.includes(
            "Avoided redundant navigation to current location"
          )
        ) {
          // But print any other errors to the console
          console.log(err);
        }
      });
    },
    //set expire date on admin key value
    setWithExpiry(key, value, ttl) {
      const now = new Date();

      // `item` is an object which contains the original value
      // as well as the time when it's supposed to expire
      const item = {
        value: value,
        expire: now.getTime() + ttl,
      };
      sessionStorage.setItem(key, JSON.stringify(item));
    },
    //checks the expirationd date on admin key stored in local storage
    getWithExpire(key) {
      const itemStr = localStorage.getItem(key);
      // if the item doesn't exist, return null
      if (!itemStr) {
        return null;
      }
      const item = JSON.parse(itemStr);
      const now = new Date();
      // compare the expiry time of the item with the current time
      if (now.getTime() > item.expire) {
        // If the item is expired, delete the item from storage
        // and return null
        localStorage.removeItem(key);
        return null;
      }
      return item.value;
    },
  },
  mounted() {
    document.title = 'შესვლა'
    if(this.getWithExpire('access')){
      this.adminPage()
    }
  },
};
</script>

<style scoped>

</style>
