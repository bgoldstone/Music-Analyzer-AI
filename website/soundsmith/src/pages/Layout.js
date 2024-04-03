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
            <Link to="/blogs">Sign In</Link>
          </li>
          <li>
            <Link to="/contact">Mood Analysis</Link>
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