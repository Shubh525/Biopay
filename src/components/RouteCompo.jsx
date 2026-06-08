import { createBrowserRouter,createRoutesFromElements,Route } from "react-router-dom"
import Layout from "../Layout"
import {Home} from "./Home"
import DeviceDetails from "./DeviceDetails"
import AboutUs from "./AboutUs"
import Diagnostic from "./Diagnostic"
import Login from "./Login"
import {Register} from "./Register"
import HomePage from "./HomePage"
import ContactUs from "./contactUs"
import Services from "./Services";
import Work from "./Work";
export const RouteCompo=createBrowserRouter(
    createRoutesFromElements(
       <Route path='/' element={<Layout/>}>
        <Route path="/home" element={<Home/>}/>
        <Route path="/deviceDetails" element={<DeviceDetails />} />
        <Route path="/diagnostic" element={<Diagnostic />} />
        <Route path="/aboutUs" element={<AboutUs />} />
        <Route index element={<Home />} />

        <Route path="/homepage" element={<HomePage />} />
         <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/contactUs" element={<ContactUs/>} />
          <Route path="/services" element={<Services />} />
         <Route path="/work" element={<Work />} />
       </Route> 
    )
)


