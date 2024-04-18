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
            <Link to="/contact">Sign In</Link>
          </li>
          <li>
            <Link to="/blogs">Mood Analysis</Link>
          </li>
          <li>
            <Link to="/loading">Loading</Link>
          </li>
          <li>
            <Link to="/VSM">VSM</Link>
          </li>

        </ul>
      </nav>

      <Outlet />
    </>
  )
};

export default Layout;