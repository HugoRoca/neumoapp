import { useState } from 'react'
import MainLayout from '@/components/Layout/MainLayout'
import Card from '@/components/UI/Card'

/**
 * Book Appointment Page
 * Allows users to book a new medical appointment
 * TO BE IMPLEMENTED: Full booking form with calendar and time slots
 */
const BookAppointment = () => {
  return (
    <MainLayout>
      <div className="px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Agendar Cita</h1>
          <p className="text-gray-600 mt-2">
            Selecciona el hospital, especialidad, fecha y horario para tu cita
          </p>
        </div>

        <Card title="Formulario de Reserva" className="max-w-4xl mx-auto">
          <div className="text-center py-12 text-gray-500">
            <p>Implementación pendiente...</p>
            <p className="text-sm mt-2">Este componente incluirá el formulario completo de reserva</p>
          </div>
        </Card>
      </div>
    </MainLayout>
  )
}

export default BookAppointment

