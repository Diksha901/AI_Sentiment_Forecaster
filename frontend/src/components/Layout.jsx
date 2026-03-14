import React from 'react';
import { NavLink } from 'react-router-dom';
import { BarChart3 } from 'lucide-react';

const Navbar = () => {
    return (
        <header className="fixed top-0 w-full z-50 border-b border-white/5 bg-background-dark/80 backdrop-blur-md px-6 py-4 lg:px-20">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                <NavLink to="/" className="flex items-center gap-3">
                    <div className="text-primary">
                        <BarChart3 className="w-8 h-8" />
                    </div>
                    <h2 className="text-xl font-bold tracking-tight">TrendAI</h2>
                </NavLink>
                <nav className="hidden md:flex flex-1 justify-center gap-8">
                    <a className="text-sm font-medium hover:text-primary transition-colors cursor-pointer text-slate-300">Product</a>
                    <a className="text-sm font-medium hover:text-primary transition-colors cursor-pointer text-slate-300">Solutions</a>
                    <a className="text-sm font-medium hover:text-primary transition-colors cursor-pointer text-slate-300">Pricing</a>
                    <a className="text-sm font-medium hover:text-primary transition-colors cursor-pointer text-slate-300">About</a>
                </nav>
                <div className="flex items-center gap-4">
                    <NavLink to="/login" className="hidden sm:block text-sm font-bold hover:text-primary px-4 text-slate-300">Login</NavLink>
                    <NavLink to="/signup" className="bg-primary text-background-dark rounded-lg px-5 py-2 text-sm font-bold hover:brightness-110 transition-all shadow-[0_0_20px_rgba(13,204,242,0.3)]">
                        Get Started
                    </NavLink>
                </div>
            </div>
        </header>
    );
};

const Footer = () => {
    return (
        <footer className="border-t border-white/5 px-6 lg:px-20 py-20 bg-background-dark">
            <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12 text-center md:text-left">
                <div className="flex flex-col gap-6">
                    <div className="flex items-center justify-center md:justify-start gap-3">
                        <div className="text-primary">
                            <BarChart3 className="w-8 h-8" />
                        </div>
                        <h2 className="text-xl font-bold tracking-tight">TrendAI</h2>
                    </div>
                    <p className="text-slate-400 text-sm leading-relaxed">
                        Empowering brands with predictive intelligence to stay relevant in a fast-moving world.
                    </p>
                </div>
                <div>
                    <h5 className="font-bold mb-6">Product</h5>
                    <ul className="flex flex-col gap-3 text-sm text-slate-400">
                        <li><a className="hover:text-primary transition-colors cursor-pointer">Analysis</a></li>
                        <li><a className="hover:text-primary transition-colors cursor-pointer">Forecasting</a></li>
                        <li><a className="hover:text-primary transition-colors cursor-pointer">API</a></li>
                    </ul>
                </div>
                <div>
                    <h5 className="font-bold mb-6">Company</h5>
                    <ul className="flex flex-col gap-3 text-sm text-slate-400">
                        <li><a className="hover:text-primary transition-colors cursor-pointer">About Us</a></li>
                        <li><a className="hover:text-primary transition-colors cursor-pointer">Careers</a></li>
                        <li><a className="hover:text-primary transition-colors cursor-pointer">Privacy</a></li>
                    </ul>
                </div>
                <div>
                    <h5 className="font-bold mb-6">Support</h5>
                    <ul className="flex flex-col gap-3 text-sm text-slate-400">
                        <li><NavLink to="/help" className="hover:text-primary transition-colors">Help Center</NavLink></li>
                        <li><a className="hover:text-primary transition-colors cursor-pointer">Documentation</a></li>
                        <li><a className="hover:text-primary transition-colors cursor-pointer">Contact</a></li>
                    </ul>
                </div>
            </div>
            <div className="max-w-7xl mx-auto mt-20 pt-8 border-t border-white/5 text-center text-slate-500 text-xs">
                © 2024 TrendAI. Predicted with precision. All rights reserved.
            </div>
        </footer>
    );
};

const Layout = ({ children }) => {
    return (
        <div className="min-h-screen bg-background-dark text-slate-100 selection:bg-primary/30">
            <Navbar />
            <main className="pt-24 min-h-screen">
                {children}
            </main>
            <Footer />
        </div>
    );
};

export default Layout;
