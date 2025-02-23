export default function Footer() {
	return (
		<footer className="bg-red-600 text-white p-6 mt-10 flex justify-center items-center flex-col">
			<p className="text-lg font-semibold">
				https://github.com/Code-Of-The-Future-Hackathon/code-of-the-future-25-false-positive
			</p>
			<p className="text-lg font-semibold mt-3">
				© {new Date().getFullYear()} Всички права запазени.
			</p>
		</footer>
	);
}
