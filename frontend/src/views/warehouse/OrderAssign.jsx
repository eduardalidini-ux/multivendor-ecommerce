import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Swal from 'sweetalert2'

import useAxios from '../../utils/useAxios'

function OrderAssign() {
    const axios = useAxios()
    const param = useParams()

    const [order, setOrder] = useState(null)
    const [couriers, setCouriers] = useState([])
    const [selectedCourierUserId, setSelectedCourierUserId] = useState('')
    const [shipment, setShipment] = useState(null)

    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true)
            try {
                const [courierRes, trackRes] = await Promise.all([
                    axios.get('warehouse/couriers/'),
                    axios.get(`warehouse/track/order/${param.orderOid}/`)
                ])

                setCouriers(courierRes.data || [])
                setOrder(trackRes.data?.order || null)
                setShipment(trackRes.data?.shipment || null)
            } catch (e) {
                setOrder(null)
                setShipment(null)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [param.orderOid])

    const assignCourier = async () => {
        if (!selectedCourierUserId) {
            Swal.fire({ icon: 'error', title: 'Please select a courier' })
            return
        }

        setSaving(true)
        try {
            const payload = {}
            payload.order_oid = order?.oid || param.orderOid
            payload.courier_user_id = selectedCourierUserId

            const res = await axios.post('warehouse/assign/', payload)
            setShipment(res.data)
            Swal.fire({ icon: 'success', title: 'Courier assigned' })
        } catch (e) {
            Swal.fire({ icon: 'error', title: e?.response?.data?.message || 'Failed to assign courier' })
        } finally {
            setSaving(false)
        }
    }

    return (
        <div className='container mt-5' style={{ marginBottom: 150 }}>
            <div className='d-flex align-items-center justify-content-between mb-3'>
                <h3 className='mb-0'>Assign Courier</h3>
                <div>
                    <Link className='btn btn-outline-secondary me-2' to='/warehouse/orders'>Back to Orders</Link>
                    {order?.oid && (
                        <Link className='btn btn-outline-primary' to={`/track/order/${order.oid}`}>Open Tracking</Link>
                    )}
                </div>
            </div>

            {loading && <div className='text-center'>Loading...</div>}

            {!loading && !order && (
                <div className='alert alert-danger'>Order not found or you do not have access.</div>
            )}

            {!loading && order && (
                <>
                    <div className='rounded shadow p-3 bg-white mb-4'>
                        <h5 className='mb-3'>Order #{order.oid}</h5>
                        <div className='row'>
                            <div className='col-lg-6'>
                                <div className='fw-bold'>{order.full_name}</div>
                                <div className='text-muted'>{order.email}</div>
                                <div className='text-muted'>{order.mobile}</div>
                            </div>
                            <div className='col-lg-6'>
                                <div>{order.address}</div>
                                <div className='text-muted'>{[order.city, order.state, order.country].filter(Boolean).join(', ')}</div>
                            </div>
                        </div>
                    </div>

                    <div className='rounded shadow p-3 bg-white mb-4'>
                        <h5 className='mb-3'>Assign</h5>
                        <div className='row align-items-end'>
                            <div className='col-lg-8 mb-3'>
                                <label className='form-label'>Courier</label>
                                <select className='form-select' value={selectedCourierUserId} onChange={(e) => setSelectedCourierUserId(e.target.value)}>
                                    <option value=''>Select courier</option>
                                    {couriers.map((c) => (
                                        <option key={c.id} value={c.id}>{c.full_name || c.email}</option>
                                    ))}
                                </select>
                            </div>
                            <div className='col-lg-4 mb-3'>
                                <button className='btn btn-primary w-100' onClick={assignCourier} disabled={saving}>
                                    {saving ? 'Assigning...' : 'Assign Courier'}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className='rounded shadow p-3 bg-white'>
                        <h5 className='mb-3'>Shipment Timeline</h5>
                        {!shipment && <div className='text-muted'>No shipment yet.</div>}
                        {shipment && (
                            <>
                                <div className='mb-2'><span className='fw-bold'>Status:</span> {shipment.status}</div>
                                <ul className='list-group'>
                                    {(shipment.events || []).map((e) => (
                                        <li key={e.id} className='list-group-item d-flex justify-content-between align-items-start'>
                                            <div>
                                                <div className='fw-bold'>{e.event_type}</div>
                                                {e.message && <div className='text-muted'>{e.message}</div>}
                                            </div>
                                            <div className='text-muted' style={{ fontSize: 12 }}>{new Date(e.created_at).toLocaleString()}</div>
                                        </li>
                                    ))}
                                    {(!shipment.events || shipment.events.length === 0) && (
                                        <li className='list-group-item text-muted'>No events yet.</li>
                                    )}
                                </ul>
                            </>
                        )}
                    </div>
                </>
            )}
        </div>
    )
}

export default OrderAssign
