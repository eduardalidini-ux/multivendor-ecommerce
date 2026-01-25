import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Swal from 'sweetalert2'

import useAxios from '../../utils/useAxios'

function ShipmentDetail() {
    const axios = useAxios()
    const param = useParams()

    const [shipment, setShipment] = useState(null)
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [note, setNote] = useState('')

    const fetchShipment = async () => {
        setLoading(true)
        try {
            const res = await axios.get(`warehouse/courier/shipment/${param.shipmentId}/`)
            setShipment(res.data || null)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchShipment()
    }, [param.shipmentId])

    const updateStatus = async (status) => {
        if (!shipment) return

        setSaving(true)
        try {
            const payload = note?.trim() ? { status, message: note.trim() } : { status }
            const res = await axios.patch(`warehouse/courier/shipment/${shipment.id}/status/`, payload)
            setShipment(res.data)
            setNote('')
            Swal.fire({ icon: 'success', title: 'Status updated' })
        } catch (e) {
            Swal.fire({ icon: 'error', title: e?.response?.data?.message || 'Failed to update status' })
        } finally {
            setSaving(false)
        }
    }

    const allowedNext = {
        assigned: ['picked_up', 'failed'],
        picked_up: ['out_for_delivery', 'failed', 'returned'],
        out_for_delivery: ['delivered', 'failed', 'returned'],
        failed: ['returned'],
        returned: [],
        delivered: [],
        pending_assignment: [],
    }

    const canSetStatus = (targetStatus) => {
        if (!shipment?.status) return false
        if (saving) return false
        if (shipment.status === targetStatus) return false
        return (allowedNext[shipment.status] || []).includes(targetStatus)
    }

    return (
        <div className='container mt-5' style={{ marginBottom: 150 }}>
            <div className='d-flex align-items-center justify-content-between mb-3'>
                <h3 className='mb-0'>Shipment Detail</h3>
                <div>
                    <Link className='btn btn-outline-secondary me-2' to='/courier/dashboard'>Back</Link>
                    {shipment?.order?.oid && (
                        <Link className='btn btn-outline-primary' to={`/track/order/${shipment.order.oid}`}>Open Tracking</Link>
                    )}
                </div>
            </div>

            {loading && <div className='text-center'>Loading...</div>}

            {!loading && !shipment && (
                <div className='alert alert-danger'>Shipment not found.</div>
            )}

            {!loading && shipment && (
                <>
                    <div className='rounded shadow p-3 bg-white mb-4'>
                        <div className='row'>
                            <div className='col-lg-6'>
                                <h5 className='mb-2'>Order #{shipment.order?.oid}</h5>
                                <div className='text-muted'>{shipment.order?.full_name}</div>
                                <div className='text-muted'>{shipment.order?.email}</div>
                                <div className='text-muted'>{shipment.order?.mobile}</div>
                            </div>
                            <div className='col-lg-6'>
                                <h6 className='mb-2'>Destination</h6>
                                <div>{shipment.order?.address}</div>
                                <div className='text-muted'>{[shipment.order?.city, shipment.order?.state, shipment.order?.country].filter(Boolean).join(', ')}</div>
                            </div>
                        </div>
                        <div className='mt-3'><span className='fw-bold'>Current status:</span> {shipment.status}</div>
                    </div>

                    <div className='rounded shadow p-3 bg-white mb-4'>
                        <h5 className='mb-3'>Update Status</h5>
                        <div className='mb-3'>
                            <label className='form-label'>Note (optional)</label>
                            <input
                                className='form-control'
                                value={note}
                                onChange={(e) => setNote(e.target.value)}
                                placeholder='E.g. Customer not available, left at reception...'
                                disabled={saving}
                            />
                        </div>
                        <div className='d-flex flex-wrap gap-2'>
                            <button className='btn btn-outline-primary me-2 mb-2' disabled={!canSetStatus('picked_up')} onClick={() => updateStatus('picked_up')}>Picked Up</button>
                            <button className='btn btn-outline-primary me-2 mb-2' disabled={!canSetStatus('out_for_delivery')} onClick={() => updateStatus('out_for_delivery')}>Out For Delivery</button>
                            <button className='btn btn-outline-success me-2 mb-2' disabled={!canSetStatus('delivered')} onClick={() => updateStatus('delivered')}>Delivered</button>
                            <button className='btn btn-outline-danger me-2 mb-2' disabled={!canSetStatus('failed')} onClick={() => updateStatus('failed')}>Failed</button>
                            <button className='btn btn-outline-secondary me-2 mb-2' disabled={!canSetStatus('returned')} onClick={() => updateStatus('returned')}>Returned</button>
                        </div>
                        <div className='text-muted' style={{ fontSize: 12 }}>
                            Only use "Delivered" when the package is successfully delivered.
                        </div>
                    </div>

                    <div className='rounded shadow p-3 bg-white'>
                        <h5 className='mb-3'>Timeline</h5>
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
                    </div>
                </>
            )}
        </div>
    )
}

export default ShipmentDetail
