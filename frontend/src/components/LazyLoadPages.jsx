import { lazy } from "react";

const Home = lazy(() =>
    import("./Home").then((module) => ({
        default: module.Home,
    }))
);
const DeviceDetails = lazy(() => import("./DeviceDetails"));
const AboutUs = lazy(() => import("./AboutUs"));
const Diagnostic = lazy(() => import("./Diagnostic"));
const Login = lazy(() => import("./Login"));
const Register = lazy(() =>
    import("./Register").then((module) => ({
        default: module.Register,
    }))
);
const HomePage = lazy(() => import("./HomePage"));
const ContactUs = lazy(() => import("./ContactUs"));
const Services = lazy(() => import("./Services"));
const Work = lazy(() => import("./Work"));
export {
    Home,
    DeviceDetails,
    AboutUs,
    Diagnostic,
    Login,
    Register,
    HomePage,
    ContactUs,
    Services,
    Work,
};