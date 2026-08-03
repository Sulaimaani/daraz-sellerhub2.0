import Link from "next/link";

export default function MarketingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="header-gradient py-6 px-8 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Daraz Seller SaaS</h1>
        <nav className="flex space-x-4">
          <Link
            href="/login"
            className="text-white hover:text-[var(--color-brand-primary-light)]"
          >
            Login
          </Link>
          <Link
            href="/signup"
            className="bg-[var(--color-brand-primary)] text-white px-4 py-2 rounded-md font-medium hover:bg-[var(--color-brand-primary-dark)]"
          >
            Sign Up
          </Link>
        </nav>
      </header>

      <main className="flex-grow flex flex-col items-center justify-center p-8 text-center">
        <h2 className="text-5xl font-extrabold mb-6">
          Manage Your Daraz Store Like a Pro
        </h2>
        <p className="text-xl text-gray-600 mb-10 max-w-2xl">
          Connect your store, manage orders, print labels, audit finance, and
          track return claims from one central dashboard.
        </p>
        <Link
          href="/signup"
          className="bg-[var(--color-brand-primary)] text-white text-lg px-8 py-4 rounded-md font-bold hover:bg-[var(--color-brand-primary-dark)] shadow-lg transition-all"
        >
          Get Started for Free
        </Link>
      </main>

      <footer className="py-6 text-center text-gray-500 border-t border-[var(--color-border-card)]">
        &copy; {new Date().getFullYear()} Daraz Seller SaaS. All rights
        reserved.
      </footer>
    </div>
  );
}
