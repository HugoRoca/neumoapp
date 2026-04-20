/**
 * Reusable Card Component
 * @param {string} [bodyClassName] - Padding del cuerpo (default px-6; usar px-3 sm:px-6 en formularios móviles)
 */
const Card = ({ children, className = '', bodyClassName, title, subtitle, ...props }) => {
  const bodyPad = bodyClassName ?? 'px-6 py-4'
  return (
    <div
      className={`bg-white rounded-lg shadow-md overflow-hidden ${className}`}
      {...props}
    >
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-200">
          {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
          {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
        </div>
      )}
      <div className={bodyPad}>{children}</div>
    </div>
  )
}

export default Card

