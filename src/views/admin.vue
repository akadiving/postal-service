<template>
  <div id="admin" class="text-center">
    <Header 
    v-bind:drawer='drawer'
    @menu='menu' />
    <v-navigation-drawer v-model="drawer" app >
      <v-sheet color="grey lighten-4" class="pa-4">
        <v-avatar class="mb-4" color="blue" size="64">
          <v-icon dark x-large> mdi-account </v-icon>
        </v-avatar>

        <div v-if='adminName'>{{adminName}}</div>
        <div v-else>Admin</div>
      </v-sheet>

      <v-divider></v-divider>

      <v-list rounded>
        <v-list-item link @click="logout">
          <v-list-item-avatar color='warning'>
            <v-icon dark>mdi-logout</v-icon>
          </v-list-item-avatar>
          <v-list-item-title>გამოსვლა</v-list-item-title>
        </v-list-item>

        <v-list-item @click="items">
          <v-list-item-avatar color='purple'>
            <v-icon dark>mdi-package-variant-closed</v-icon>
          </v-list-item-avatar>
          <v-list-item-title>ამანათები</v-list-item-title>
        </v-list-item>

        <v-list-item @click="manifest">
          <v-list-item-avatar color='primary'>
            <v-icon dark>mdi-clipboard-list-outline</v-icon>
          </v-list-item-avatar>
          <v-list-item-title>მანიფესტები</v-list-item-title>
        </v-list-item>
        <v-list-item @click="close">
          <v-list-item-avatar color='green'>
            <v-icon dark>mdi-home-outline</v-icon>
          </v-list-item-avatar>
          <v-list-item-title>მთავარი გვერდი</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-container fill-height fluid>
      <v-row justify="center" align='center'>
        <v-col cols="auto" v-if="!component" id="package" class='mt-4'>
          <v-card
            height='230'
            width='245'
            size='144'
            v-ripple="{ class: `secondary--text`}"
            @click="addItem"
          >
            <v-avatar
            class="mt-3"
            size="144"
            tile
            >
              <v-img src="../assets/package-box-svgrepo-com.svg"></v-img>
            </v-avatar>
            <v-card-text>
              <v-row align="center">
                <v-col class="text-h6 text--primary"
                cols="12">
                  ამანათის დამატება
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          
        </v-col>
        <v-col cols="auto" v-if="!component" id="package" class='mt-4'>
          <v-card
            height='230'
            width='245'
            size='144'
            v-ripple="{ class: `secondary--text`}"
            @click="addManifest"
          >
            <v-avatar
            class="mt-3"
            size="144"
            tile
            >
              <v-img src="../assets/list-svgrepo-com.svg"></v-img>
            </v-avatar>
            <v-card-text>
              <v-row align="center">
                <v-col class="text-h6 text--primary"
                cols="12">
                  მანიფესტის დამატება
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- components -->
        <v-col cols="12" v-else>
          <transition name="fade-transition">
            <component 
            v-bind:is="component"
            :manifestID="manifestID"
            @closeComponent='close'
            @closeItems='close'
            @closeManifest='close'
            @closeManifestDetail='closeManifestDetail'
            @getManifestDetail='getManifestDetail'
            ></component>
          </transition>
        </v-col>
        <!-- components -->
      </v-row>
    </v-container>
  </div>
</template>

<script>
import router from "../router/index";
import axios from 'axios'
//import axiosInstance from '../axios.js'
import Header from '../components/header.vue'
import Items from '../components/items.vue'
import Manifest from '../components/manifest.vue'
import AddItem from '../components/addItem.vue'
import AddManifest from '../components/addManifest.vue'
import ManifestDetail from '../components/manifestDetail.vue'
import Preloader from '../components/preloader.vue'

export default {
  name: "Admin",
  props: {},
  components: {
    Header,
    'Items': Items,
    'Manifest': Manifest,
    'AddItem': AddItem,
    'ManifestDetail': ManifestDetail,
    'AddManifest':AddManifest,
    'Preloader': Preloader
  },
  data: () => ({
    adminName: '',
    errorM: "",
    admin: false,
    password: "",
    email: "",
    validLogin: true,
    passwordRules: [(v) => !!v || "Password is required"],
    emailRules: [
      (v) => !!v || "E-mail is required",
      (v) => /.+@.+\..+/.test(v) || "E-mail must be valid",
    ],
    drawer: null,
    loadTable: true,
    component: "",
    manifestID: '',
  }),

  methods: {
    //logs out by removing admin key from local storage
    logout() {
      axios.post('http://127.0.0.1:8000/api/logout/', {
        refresh_token: sessionStorage.getItem('refresh')
      })
      .then((response) => {
        console.log(response)
        //localStorage.removeItem('access')
        //localStorage.removeItem('refresh')
        sessionStorage.clear();
        this.loginPage()
      })
      .catch((error)=>{
        console.log(error)
      })
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
      const itemStr = sessionStorage.getItem(key);
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
        sessionStorage.removeItem(key);
        return null;
      }
      return item.value;
    },
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
    manifestListPage() {
      router.push({ path: "/manifest" }).catch((err) => {
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
    items() {
      if (this.component !== "Items") {
        this.component = "Items";
      } else {
        this.component = "";
      }
    },
    manifest() {
      if (this.component !== "Manifest") {
        this.component = "Manifest";
      } else {
        this.component = "";
      }
    },
    addItem() {
      if (this.component !== "AddItem") {
        this.component = "AddItem";
      } else {
        this.component = "";
      }
    },
    addManifest() {
      if (this.component !== "AddManifest") {
        this.component = "AddManifest";
      } else {
        this.component = "";
      }
    },
    ManifestDetail() {
      if (this.component !== "ManifestDetail") {
        this.component = "ManifestDetail";
      } else {
        this.component = "";
      }
    },
    getManifestDetail(id){
      this.manifestID = id
      this.ManifestDetail()
    },
    menu(){
      this.drawer = !this.drawer
    },
    close(){
      this.component = '';
    },
    closeManifestDetail(){
      this.manifest()
    },
    preload(){
      this.component = 'Preloader';
      setTimeout(()=>{
        this.component = '';
      }, 1000);
    },
    //get current user
    getUser(){
      let accessToken = JSON.parse(sessionStorage.getItem('access'))
      const baseURL = `https://postal-service-test.herokuapp.com/users/me/`;
      const options = {
          method: 'GET',
          baseURL: baseURL,
          timeout: 5000,
          headers: {
              Authorization: 'Bearer ' + accessToken.value
          }, 
      };
      axios(options)
      .then((response) => {
        console.log(response)
        sessionStorage.setItem('company_name', response.data.company_name)
        this.adminName = sessionStorage.getItem('company_name')
      })
      .catch((error) => {
        this.errorM = error.response.data.detail
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
        if(error.response.data.detail == 'Given token not valid for any token type' || error.response.data.detail == 'User is inactive'){
          this.logout()
        }
      })
    }
  },
  mounted() {
    document.title = 'მართვის პანელი'
    if(!this.getWithExpire('access')){
      this.loginPage()
    }
    this.getUser()
    
  },
};
</script>

<style scoped>
#package{
  cursor: pointer;
  transition: all .2s ease-in-out; 
}
#package:hover {
  transform: scale(1.05);
}
</style>
