import ReactMarkdown from 'react-markdown'

/** react-markdown inyecta `node` (mdast); no debe propagarse al DOM. */
function omitNode(mdProps) {
  // eslint-disable-next-line no-unused-vars -- `node` es metadato del árbol MD, no un prop HTML
  const { node, ...props } = mdProps
  return props
}

/**
 * Renderiza respuestas del asistente como Markdown (negritas, listas, enlaces).
 * Sin HTML crudo: el modelo solo puede usar sintaxis MD estándar.
 */
export default function AssistantMarkdown({ content }) {
  return (
    <div className="assistant-md break-words">
      <ReactMarkdown
        components={{
          p: (p) => <p className="mb-2 last:mb-0" {...omitNode(p)} />,
          strong: (p) => <strong className="font-semibold text-gray-900" {...omitNode(p)} />,
          em: (p) => <em className="italic text-gray-800" {...omitNode(p)} />,
          ul: (p) => <ul className="my-2 list-disc space-y-1 pl-5" {...omitNode(p)} />,
          ol: (p) => <ol className="my-2 list-decimal space-y-1 pl-5" {...omitNode(p)} />,
          li: (p) => <li className="break-words pl-0.5" {...omitNode(p)} />,
          a: (p) => (
            <a
              className="font-medium text-primary-700 underline decoration-primary-300 underline-offset-2 hover:text-primary-800"
              target="_blank"
              rel="noopener noreferrer"
              {...omitNode(p)}
            />
          ),
          code: (p) => {
            // `inline` lo añade react-markdown; no es un atributo HTML válido en <code>
            // eslint-disable-next-line no-unused-vars -- separar de props del DOM
            const { className, children, inline, ...rest } = omitNode(p)
            const isBlock = className?.includes('language-')
            if (isBlock) {
              return (
                <pre className="my-2 overflow-x-auto rounded-lg bg-slate-100 p-3 text-sm">
                  <code className={className} {...rest}>
                    {children}
                  </code>
                </pre>
              )
            }
            return (
              <code className="rounded bg-slate-100 px-1 py-0.5 font-mono text-[0.9em] text-gray-800" {...rest}>
                {children}
              </code>
            )
          },
          h1: (p) => <h3 className="mb-2 mt-3 text-base font-bold text-gray-900 first:mt-0" {...omitNode(p)} />,
          h2: (p) => <h3 className="mb-2 mt-3 text-base font-bold text-gray-900 first:mt-0" {...omitNode(p)} />,
          h3: (p) => <h3 className="mb-2 mt-3 text-sm font-bold text-gray-900 first:mt-0" {...omitNode(p)} />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
