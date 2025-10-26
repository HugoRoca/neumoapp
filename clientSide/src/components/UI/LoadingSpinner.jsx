/**
 * Loading Spinner Component
 */
const LoadingSpinner = ({ size = 'md', message = 'Cargando...' }) => {
  const sizes = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  }

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div
        className={`animate-spin rounded-full border-b-2 border-primary-600 ${sizes[size]}`}
      ></div>
      {message && (
        <p className="mt-4 text-gray-600 text-sm">{message}</p>
      )}
    </div>
  )
}

export default LoadingSpinner

