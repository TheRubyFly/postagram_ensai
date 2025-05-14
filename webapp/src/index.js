import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import axios from 'axios'
// Importing the Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
axios.defaults.baseURL = "http://tf-lb-20250514135256765400000003-2117103507.us-east-1.elb.amazonaws.com:8080"// <------ A modifier quand vous aller tester avec vos instances EC2 et votre load balancer !!!

//"http://tf-lb-20250514135256765400000003-2117103507.us-east-1.elb.amazonaws.com:8080"

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
