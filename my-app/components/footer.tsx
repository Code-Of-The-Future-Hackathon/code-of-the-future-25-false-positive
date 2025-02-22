export default function Footer() {
	return (
		<footer className="bg-red-600 text-white p-6 mt-10 flex justify-center items-center">
			<p className="text-lg font-semibold">
				© {new Date().getFullYear()} Всички права запазени.
			</p>
		</footer>
	);
}
