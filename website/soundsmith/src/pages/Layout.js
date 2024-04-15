import { Outlet, Link } from "react-router-dom";
import React from 'react';


const Layout = () => {
  return (
    <>
      <nav>
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/login">Sign In</Link>
          </li>
          <li>
            <Link to="/moos">Mood Analysis</Link>
          </li>
          <li>
            <Link to="/loading">Loading</Link>
          </li>
        </ul>
      </nav>

      <Outlet />
    </>
  )
};

export default Layout;